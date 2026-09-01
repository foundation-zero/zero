import asyncio
import json
import logging
import re
from typing import Literal

from faststream import FastStream
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)
from zero_modbus_bridge.bridge import ModbusBridge
from zero_modbus_bridge.io import ModbusTopic
from zero_modbus_bridge.settings import MqttSettings
from zero_modbus_bridge.stub import Stub

from zero_power_tags.io import (
    BridgeSpec,
    build_asyncapi,
    create_publisher,
    read_modbus_bridge_specs,
    read_topics_metadata,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)

dynamic_settings_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    env_nested_delimiter="__",
    env_prefix="",
    extra="allow",
)


def _panel_field_key(panel: str, field: Literal["host", "port"]) -> str:
    """Env key for one gateway field (`10P0.1` → `host_10p0_1`)."""
    suffix = re.sub(r"[^a-z0-9]+", "_", panel.lower()).strip("_")
    return f"{field}_{suffix}"


class PowerTagsSettings(BaseSettings):
    model_config = dynamic_settings_config

    modbus_panels: dict[str, str] = {}

    def field_for(self, panel: str, field: Literal["host", "port"]) -> str | None:
        """Configured value for ``panel``'s ``field``, or None when unset."""
        return self.modbus_panels.get(_panel_field_key(panel, field))


class BridgeEndpoint(BaseModel):
    """Resolved gateway address for one bridge spec."""

    spec: BridgeSpec
    host: str
    port: int


def _parse_port(panel: str, port_raw: str) -> int:
    """Parse and range-check a configured port; raises on anything outside 1..65535."""
    port = int(port_raw)
    if not 1 <= port <= 65535:
        raise ValueError(
            f"Invalid port {port} for panel {panel} ({_panel_field_key(panel, 'port')}): "
            "must be between 1 and 65535"
        )
    return port


def configured_modbus_ports(
    settings: PowerTagsSettings, specs: list[BridgeSpec]
) -> dict[str, int | None]:
    """Per-panel port override from `MODBUS_PANELS__port_<panel>`; None when unset."""
    return {
        spec.panel: _parse_port(spec.panel, port_raw)
        if (port_raw := settings.field_for(spec.panel, "port"))
        else None
        for spec in specs
    }


def resolve_bridge_endpoints(
    settings: PowerTagsSettings, specs: list[BridgeSpec], default_port: int
) -> list[BridgeEndpoint]:
    """Resolve gateway addresses; every panel needs ``host_<PANEL>`` set."""
    missing = sorted(
        spec.panel for spec in specs if not settings.field_for(spec.panel, "host")
    )
    if missing:
        expected = ", ".join(_panel_field_key(panel, "host") for panel in missing)
        raise ValueError(f"Missing Modbus gateway configuration: {expected}")

    ports = configured_modbus_ports(settings, specs)
    endpoints: list[BridgeEndpoint] = []
    for spec in specs:
        host = settings.field_for(spec.panel, "host")
        if host is None:  # unreachable: guaranteed non-missing above
            raise ValueError(f"Missing host for panel {spec.panel}")
        panel_port = ports[spec.panel]
        endpoints.append(
            BridgeEndpoint(
                spec=spec,
                host=host,
                port=panel_port if panel_port is not None else default_port,
            )
        )
    return endpoints


def stub_ports(
    settings: PowerTagsSettings, specs: list[BridgeSpec], base_port: int
) -> dict[str, int]:
    """Local ports for the stub servers.

    Honors explicit `MODBUS_PORT_<PANEL>` overrides; panels without one are
    spread over consecutive ports starting at base_port so the servers can
    coexist on a single machine.
    """
    configured = configured_modbus_ports(settings, specs)
    resolved: dict[str, int] = {}
    for index, spec in enumerate(specs):
        override = configured[spec.panel]
        resolved[spec.panel] = override if override is not None else base_port + index
    return resolved


def local_topic_groups(
    settings: PowerTagsSettings, specs: list[BridgeSpec], base_port: int
) -> list[tuple[list[ModbusTopic], int]]:
    """One `(topics, port)` group per panel, ready for the local stub servers."""
    ports = stub_ports(settings, specs, base_port)
    return [(spec.topics, ports[spec.panel]) for spec in specs]


class RunCmd(MqttSettings):
    modbus_port: int = 502
    modbus_probe_interval: int = 10

    async def cli_cmd(self) -> None:
        broker = self.make_broker()
        specs = read_modbus_bridge_specs()
        endpoints = resolve_bridge_endpoints(
            PowerTagsSettings(), specs, self.modbus_port
        )
        publisher = create_publisher(broker, specs)
        bridges = [
            ModbusBridge.from_address(
                endpoint.host,
                endpoint.port,
                publisher,
                endpoint.spec.topics,
                self.modbus_probe_interval,
            )
            for endpoint in endpoints
        ]
        logger.info(
            "Starting %d modbus bridge(s): %s",
            len(bridges),
            ", ".join(f"{e.spec.panel}→{e.host}:{e.port}" for e in endpoints),
        )

        app = FastStream(broker)

        async def run_bridges() -> None:
            async with asyncio.TaskGroup() as task_group:
                for bridge in bridges:
                    task_group.create_task(bridge.run())

        app.after_startup(run_bridges)
        await app.run()


class StubCmd(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    modbus_port: int = 502
    default_register_value: float = 0.0

    def cli_cmd(self) -> None:
        specs = read_modbus_bridge_specs()
        stub = Stub.from_topic_groups(
            local_topic_groups(PowerTagsSettings(), specs, self.modbus_port),
            default_value=0,
            float_default=self.default_register_value,
        )
        for server in stub.servers:
            logger.info("Stub serving on %s:%d", server.host, server.port)
        stub.run()


class TuiCmd(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    modbus_port: int = 502
    default_register_value: float = 0.0

    def cli_cmd(self) -> None:
        from zero_modbus_bridge.tui import (
            run_tui,
        )  # heavy TUI-only dep, import on demand

        specs = read_modbus_bridge_specs()
        run_tui(
            local_topic_groups(PowerTagsSettings(), specs, self.modbus_port),
            default_value=0,
            float_default=self.default_register_value,
        )


class AsyncApiCmd(BaseSettings):
    title: str = "Power Tags"
    version: str = "1.0.0"

    def cli_cmd(self) -> None:
        # FastStream derives specs from publishers registered on a broker,
        # so print-asyncapi registers the same publisher shape as run.
        print(
            json.dumps(
                build_asyncapi(self.title, self.version), indent=2, ensure_ascii=False
            )
        )


class MetadataCmd(BaseSettings):
    def cli_cmd(self) -> None:
        print(json.dumps(read_topics_metadata(), indent=2, ensure_ascii=False))


class ZeroPowerTags(BaseSettings, cli_kebab_case=True):
    model_config = dynamic_settings_config

    run: CliSubCommand[RunCmd]
    stub: CliSubCommand[StubCmd]
    tui: CliSubCommand[TuiCmd]
    print_asyncapi: CliSubCommand[AsyncApiCmd]
    print_metadata: CliSubCommand[MetadataCmd]

    def cli_cmd(self) -> None:
        try:
            CliApp.run_subcommand(self)
        except KeyboardInterrupt:
            pass
