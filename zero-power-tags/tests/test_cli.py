import logging
import os
import re
from contextlib import asynccontextmanager

import pytest
from faststream.mqtt import MQTTBroker
from zero_modbus_bridge.bridge import ModbusBridge
from zero_mqtt.broker import RecoveringBroker

from zero_power_tags import cli
from zero_power_tags.cli import (
    PowerTagsSettings,
    RunCmd,
    configured_modbus_ports,
    deployed_specs,
    local_topic_groups,
    resolve_bridge_endpoints,
    stub_ports,
)
from zero_power_tags.io import BridgeSpec, read_modbus_bridge_specs


@pytest.fixture(autouse=True)
def _no_modbus_env(monkeypatch: pytest.MonkeyPatch):
    for key in list(os.environ):
        if key.startswith("MODBUS_PANELS__"):
            monkeypatch.delenv(key)


def _spec(panel: str) -> BridgeSpec:
    return BridgeSpec(panel=panel, topics=[])


def _settings(**panels: str) -> PowerTagsSettings:
    # `_env_file=None` keeps the .env out of these unit tests.
    return PowerTagsSettings(_env_file=None, modbus_panels=panels)  # type: ignore[call-arg]


class TestConfiguredModbusPorts:
    def test_unset_panels_are_none(self):
        settings = _settings(port_10p0_1="5020")
        specs = [_spec("10P0-1"), _spec("10P1")]
        assert configured_modbus_ports(settings, specs) == {
            "10P0-1": 5020,
            "10P1": None,
        }

    def test_invalid_port_raises(self):
        settings = _settings(port_10p0_1="not-a-port")
        with pytest.raises(ValueError):
            configured_modbus_ports(settings, [_spec("10P0-1")])


class TestResolveBridgeEndpoints:
    def test_resolves_host_and_default_port(self):
        settings = _settings(host_10p0_1="192.168.0.10")
        endpoints = resolve_bridge_endpoints(
            settings, [_spec("10P0-1")], default_port=502
        )
        assert endpoints[0].host == "192.168.0.10"
        assert endpoints[0].port == 502
        assert endpoints[0].spec.panel == "10P0-1"

    def test_panel_port_overrides_default(self):
        settings = _settings(host_10p0_1="192.168.0.10", port_10p0_1="1502")
        endpoints = resolve_bridge_endpoints(
            settings, [_spec("10P0-1")], default_port=502
        )
        assert endpoints[0].port == 1502

    def test_unconfigured_panels_are_skipped(self, caplog):
        settings = _settings(host_10p0_1="192.168.0.10")
        with caplog.at_level(logging.WARNING):
            endpoints = resolve_bridge_endpoints(
                settings, [_spec("10P0-1"), _spec("10P1")], default_port=502
            )
        assert [e.spec.panel for e in endpoints] == ["10P0-1"]
        assert "10P1" in caplog.text

    def test_no_configured_panels_raises(self):
        with pytest.raises(ValueError, match="No Modbus gateway hosts"):
            resolve_bridge_endpoints(
                _settings(), [_spec("10P0-1"), _spec("10P1")], default_port=502
            )

    def test_empty_host_counts_as_unconfigured(self):
        settings = _settings(host_10p0_1="")
        with pytest.raises(ValueError, match="No Modbus gateway hosts"):
            resolve_bridge_endpoints(settings, [_spec("10P0-1")], default_port=502)


class TestDeployedSpecs:
    def test_keeps_only_panels_with_a_host(self):
        settings = _settings(host_10p1="192.168.0.10")
        specs = [_spec("10P0-1"), _spec("10P1")]
        assert [spec.panel for spec in deployed_specs(settings, specs)] == ["10P1"]

    def test_stub_serves_only_configured_ports(self):
        # Partial rollout: only 10P1 is deployed, pinned to stub port 15021.
        # The stub must not also spread the undeployed 10P0-3 onto 15021.
        settings = _settings(host_10p1="stub", port_10p1="15021")
        specs = [_spec("10P0-1"), _spec("10P0-3"), _spec("10P1")]
        served = deployed_specs(settings, specs) or specs
        assert stub_ports(settings, served, base_port=15020) == {"10P1": 15021}


class TestStubPorts:
    def test_unconfigured_panels_spread_from_base_port(self):
        specs = [_spec("10P0-1"), _spec("10P1")]
        assert stub_ports(_settings(), specs, base_port=5020) == {
            "10P0-1": 5020,
            "10P1": 5021,
        }

    def test_explicit_override_wins(self):
        settings = _settings(port_10p1="16000")
        specs = [_spec("10P0-1"), _spec("10P1")]
        assert stub_ports(settings, specs, base_port=5020) == {
            "10P0-1": 5020,
            "10P1": 16000,
        }


def test_make_broker_accepts_kwargs_on_real_broker():
    """The real MQTTBroker accepts our security + reconnect + keepalive kwargs."""
    cmd = RunCmd(
        _env_file=None,  # type: ignore[call-arg]
        mqtt_host="broker",
        mqtt_port=1883,
        mqtt_username="u",
        mqtt_password="p",
    )
    assert isinstance(cmd.make_broker(), MQTTBroker)


def test_buffer_size_covers_five_minutes_of_one_bridge():
    from zero_power_tags.cli import buffer_size_for

    assert buffer_size_for(probe_interval=10, topic_count=43) == 30 * 43
    assert buffer_size_for(probe_interval=1, topic_count=2) == 300 * 2


def test_run_cmd_default_client_id(monkeypatch):
    monkeypatch.delenv("MQTT_CLIENT_ID", raising=False)
    cmd = RunCmd(_env_file=None, mqtt_host="broker", mqtt_port=1883)  # type: ignore[call-arg]
    assert re.fullmatch(r"power-tags-[0-9a-f]{8}", cmd.mqtt_client_id)


def test_run_cmd_client_id_from_env(monkeypatch):
    monkeypatch.setenv("MQTT_CLIENT_ID", "custom-id")
    cmd = RunCmd(_env_file=None, mqtt_host="broker", mqtt_port=1883)  # type: ignore[call-arg]
    assert cmd.mqtt_client_id == "custom-id"


def test_local_topic_groups():
    assert local_topic_groups(_settings(), [_spec("10P1")], 1000) == [([], 1000)]


class _FakeApp:
    """Stands in for FastStream: records the broker and startup hooks, runs nothing."""

    def __init__(self, broker):
        self.broker = broker
        self.startup = []

    def after_startup(self, hook):
        self.startup.append(hook)

    async def run(self):
        pass


class _FakeHealth:
    """Stands in for zero-health: records the checks, serves nothing."""

    checks = {}

    def __init__(self, _settings, checks):
        _FakeHealth.checks = checks

    @asynccontextmanager
    async def serve(self):
        yield


async def test_run_cmd_runs_a_bridge_per_configured_panel_on_the_outage_broker(
    monkeypatch: pytest.MonkeyPatch,
):
    panel = read_modbus_bridge_specs()[0].panel
    monkeypatch.setattr(
        cli,
        "PowerTagsSettings",
        lambda: _settings(**{cli._panel_field_key(panel, "host"): "192.168.0.10"}),
    )
    apps: list[_FakeApp] = []
    monkeypatch.setattr(
        cli, "FastStream", lambda broker: apps.append(_FakeApp(broker)) or apps[-1]
    )
    started: list[ModbusBridge] = []

    async def fake_run(bridge: ModbusBridge) -> None:
        started.append(bridge)

    monkeypatch.setattr(ModbusBridge, "run", fake_run)
    monkeypatch.setattr(cli, "Health", _FakeHealth)
    cmd = RunCmd(_env_file=None, mqtt_host="broker", mqtt_port=1883)  # type: ignore[call-arg]

    await cmd.cli_cmd()
    for hook in apps[0].startup:
        await hook()

    broker = apps[0].broker
    assert isinstance(broker, RecoveringBroker)
    assert broker._connection_kwargs["reconnect"].max_attempts is None
    assert len(started) == 1
    assert list(_FakeHealth.checks) == ["mqtt"]
