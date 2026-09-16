import contextlib
import json
import logging
from datetime import datetime, timedelta
from typing import Literal

from aiomqtt import Client as MqttClient
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliImplicitFlag,
    CliSubCommand,
    SettingsConfigDict,
)

from thrs.control.switching import AutomationMode
from thrs.orchestration.comms import DirectivesChannels, MqttConnector
from thrs.orchestration.config import Config
from thrs.orchestration.log import setup_logging
from thrs.orchestration.module import Module
from thrs.orchestration.setup import (
    setup_control_modules,
    setup_database,
    setup_persistence_manager,
    setup_simulation_module,
)
from thrs.orchestration.simulation import SimulationUnit
from thrs.runtime.context import control_shutdown_context
from thrs.runtime.descriptions.simulation import ModeName, lookup_mode
from thrs.runtime.directives import DirectiveHandling
from thrs.runtime.liveness import Liveness
from thrs.runtime.runners.control import ControlRunner
from thrs.runtime.runners.lockstep import LockstepRunner
from thrs.runtime.runners.simulator import SimulationRunner
from thrs.runtime.runtime import Runtime

logger: logging.Logger = logging.getLogger(__name__)


class ControlCmd(BaseSettings):
    mode: ModeName
    machine_state_logging: CliImplicitFlag[bool] = True
    module_persistence: CliImplicitFlag[bool] = True
    allow_boot_without_persistence_having_active_postgres: CliImplicitFlag[bool] = False
    restore_manual_control_values: CliImplicitFlag[bool] = False

    async def cli_cmd(self) -> None:
        logger.debug("Starting control command: %s", self.mode)
        settings = Config()  # type: ignore

        liveness_check = Liveness(settings.liveness_path)

        control_mode = lookup_mode(self.mode)

        database = setup_database(
            settings,
            self.module_persistence,
            self.machine_state_logging,
        )

        persistence = await setup_persistence_manager(
            database,
            self.module_persistence,
            self.allow_boot_without_persistence_having_active_postgres,
            self.restore_manual_control_values,
        )

        async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
            connector = MqttConnector(mqtt_client)

            control_modules: list[Module] = setup_control_modules(
                connector,
                settings,
                control_mode.control_modules,
                datetime.now,
                database,
                self.machine_state_logging,
            )

            await persistence.restore_all(control_modules)

            runner = ControlRunner(control_modules, liveness_check, persistence)
            runtime = Runtime(runner, connector, timedelta(seconds=1))

            await runtime.loop.play(1)
            logger.info("Running control")

            async with control_shutdown_context(control_modules):
                await runtime.start()


class SimulationCmd(BaseSettings):
    mode: ModeName

    async def cli_cmd(self) -> None:
        logger.debug("Starting simulation command: %s", self.mode)
        settings = Config()  # type: ignore

        liveness_check = Liveness(settings.liveness_path)

        simulation_mode = lookup_mode(self.mode)

        async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
            connector = MqttConnector(mqtt_client=mqtt_client)

            if simulation_mode.simulation_description is None:
                raise ValueError("simulation must be defined for simulation mode")

            simulation_module: SimulationUnit = setup_simulation_module(
                connector,
                settings,
                simulation_mode.control_modules,
                simulation_mode.simulation_description,
            )

            runner = SimulationRunner(simulation_module, liveness_check)
            runtime = Runtime(runner, connector, simulation_module.tick_duration)

            await runtime.loop.play(1)
            logger.info("Running simulation")
            await runtime.start()


class LockstepCmd(BaseSettings):
    mode: ModeName
    machine_state_logging: CliImplicitFlag[bool] = True
    play: CliImplicitFlag[bool] = False
    module_persistence: CliImplicitFlag[bool] = True
    allow_boot_without_persistence_having_active_postgres: CliImplicitFlag[bool] = False
    restore_manual_control_values: CliImplicitFlag[bool] = False

    async def setup(self, settings: Config, mqtt_client: MqttClient) -> Runtime:
        logger.debug("Starting lockstep command: %s", self.mode)
        mode = lookup_mode(self.mode)

        connector = MqttConnector(mqtt_client)

        if mode.simulation_description is None:
            raise ValueError(
                f"Simulation must be defined for lockstep mode. Chosen mode '{self.mode}' has no simulation description."
            )

        simulation_module: SimulationUnit = setup_simulation_module(
            connector,
            settings,
            mode.control_modules,
            mode.simulation_description,
        )

        database = setup_database(
            settings,
            self.module_persistence,
            self.machine_state_logging,
        )

        persistence = await setup_persistence_manager(
            database,
            self.module_persistence,
            self.allow_boot_without_persistence_having_active_postgres,
            self.restore_manual_control_values,
        )

        control_modules: list[Module] = setup_control_modules(
            connector,
            settings,
            mode.control_modules,
            time_fn=simulation_module.time,
            database=database,
            machine_state_logging_service_enabled=self.machine_state_logging,
        )

        for module in control_modules:
            module.set_automation_mode(AutomationMode(mode="automatic"))

        await persistence.restore_all(control_modules)

        runner = LockstepRunner(control_modules, simulation_module, persistence)

        directives_channels = DirectivesChannels(connector, settings)

        directive_handling = DirectiveHandling(
            directives_channels,
            mode,
            simulation_module.time,
        )
        return Runtime(
            runner,
            connector,
            simulation_module.tick_duration,
            directive_handling,
        )

    async def cli_cmd(self) -> None:
        settings = Config()  # type: ignore

        async with (
            MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client,
        ):
            runtime = await self.setup(settings, mqtt_client)
            await runtime.clear_previous()
            logger.info("Running lockstep")

            if self.play:
                await runtime.loop.play(1)

            async with control_shutdown_context(runtime.runner.control_modules):  # type: ignore
                await runtime.start()


class AsyncApiCmd(BaseModel):
    title: str = "THRS Control"
    version: str = "1.0.0"
    # Bake a chosen MQTT topic prefix into the emitted channels, so this doc
    # (zero-mqtt-graphql's subscribe source) targets the same broker prefix as
    # the module-view/metadata/mutation specs. Defaults reproduce the
    # historical prefixes.
    devices_prefix: str | None = None
    controller_prefix: str | None = None

    def cli_cmd(self) -> None:
        # Imported lazily: faststream is a dev/test-only dependency (see
        # pyproject.toml) - spec generation is a CI/local-dev side quest,
        # not part of the runtime this image actually ships to run control.
        from thrs.spec.asyncapi import build_asyncapi  # noqa: PLC0415

        print(  # noqa: T201 - CLI output, not logging
            json.dumps(
                build_asyncapi(
                    self.title,
                    self.version,
                    self.devices_prefix,
                    self.controller_prefix,
                ),
                indent=2,
            )
        )


class ModuleMetadataCmd(BaseModel):
    """Print the metadata file for one THRS module's `{field}` topic group, so
    zero-mqtt-graphql can expose a list query for it (build_module_metadata).
    Same idea as zero-power-tags' `print-metadata`.

    `module` is any key of `all_module_descriptions()`. `kind="controller"` only
    produces output for modules with computed fields.

    --devices-prefix/--controller-prefix bake a chosen MQTT topic prefix into
    the group pattern and topics; match the prefixes given to
    print-module-view so the subscribe group and view topics line up. Omit to
    keep the historical prefixes."""

    module: str
    kind: Literal["sensors", "controller"]
    devices_prefix: str | None = None
    controller_prefix: str | None = None

    def cli_cmd(self) -> None:
        # Imported lazily for the same reason as AsyncApiCmd above.
        from thrs.spec.asyncapi import build_module_metadata  # noqa: PLC0415

        print(  # noqa: T201 - CLI output, not logging
            json.dumps(
                build_module_metadata(
                    self.module,
                    self.kind,
                    self.devices_prefix,
                    self.controller_prefix,
                ),
                indent=2,
            )
        )


class ModuleViewCmd(BaseModel):
    """Print the nested per-module view so zero-mqtt-graphql can serve
    ``modules.<module>.sensorValues`` 1:1 with thrs-api (build_module_view,
    modules_view.rs). Unlike ``print-module-metadata`` (one flat ``{field}``
    group), this lists every sensorValues field (raw and computed, overrides
    included) with its topic and per-leaf GraphQL/wire names.

    module is one of THRS's module names (thrusters, dhw, pvt, ...).

    --devices-prefix/--controller-prefix bake a chosen MQTT topic prefix into
    the emitted topics; omit them to keep the historical spec prefixes
    (simulation/thrs/controller)."""

    module: str
    devices_prefix: str | None = None
    controller_prefix: str | None = None

    def cli_cmd(self) -> None:
        # Imported lazily for the same reason as AsyncApiCmd above.
        from thrs.spec.asyncapi import build_module_view  # noqa: PLC0415

        print(  # noqa: T201 - CLI output, not logging
            json.dumps(
                build_module_view(
                    self.module, self.devices_prefix, self.controller_prefix
                ),
                indent=2,
            )
        )


class ModuleMutationsCmd(BaseModel):
    """Print the write-path contract so zero-mqtt-graphql can serve thrs-api's
    mutations 1:1. Per module: every parameter, control and automation-mode
    mutation with its GraphQL name, argument, by-alias payload key and MQTT
    state/set topics (build_module_mutations).

    module is one of THRS's module names (thrusters, dhw, pvt, ...).

    --controller-prefix bakes a chosen controller topic prefix into the
    state/set topics; omit it to keep the historical thrs/controller
    prefix."""

    module: str
    controller_prefix: str | None = None

    def cli_cmd(self) -> None:
        # Imported lazily for the same reason as AsyncApiCmd above.
        from thrs.spec.asyncapi import build_module_mutations  # noqa: PLC0415

        print(  # noqa: T201 - CLI output, not logging
            json.dumps(
                build_module_mutations(self.module, self.controller_prefix), indent=2
            )
        )


class SimulationViewCmd(BaseModel):
    """Print the simulation contract so zero-mqtt-graphql can serve thrs-api's
    simulation query, its play/pause/step directives and its per-simulation
    input mutations 1:1.

    --simulator-prefix bakes a chosen simulator topic prefix into the topics;
    omit it to keep the historical thrs/simulator prefix."""

    simulator_prefix: str | None = None

    def cli_cmd(self) -> None:
        # Imported lazily for the same reason as AsyncApiCmd above.
        from thrs.spec.asyncapi import build_simulation_view  # noqa: PLC0415

        print(  # noqa: T201 - CLI output, not logging
            json.dumps(build_simulation_view(self.simulator_prefix), indent=2)
        )


class ThrsCli(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    lockstep: CliSubCommand[LockstepCmd]
    simulation: CliSubCommand[SimulationCmd]
    control: CliSubCommand[ControlCmd]
    print_asyncapi: CliSubCommand[AsyncApiCmd]
    print_module_metadata: CliSubCommand[ModuleMetadataCmd]
    print_module_view: CliSubCommand[ModuleViewCmd]
    print_module_mutations: CliSubCommand[ModuleMutationsCmd]
    print_simulation_view: CliSubCommand[SimulationViewCmd]

    def cli_cmd(self) -> None:
        setup_logging()

        with contextlib.suppress(KeyboardInterrupt):
            CliApp.run_subcommand(self)
