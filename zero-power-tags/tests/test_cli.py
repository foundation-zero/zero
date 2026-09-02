import os

import pytest

from zero_power_tags.cli import (
    PowerTagsSettings,
    configured_modbus_ports,
    configured_specs,
    resolve_bridge_endpoints,
    stub_ports,
)
from zero_power_tags.io import BridgeSpec


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
        specs = [_spec("10P0.1"), _spec("10P1")]
        assert configured_modbus_ports(settings, specs) == {
            "10P0.1": 5020,
            "10P1": None,
        }

    def test_invalid_port_raises(self):
        settings = _settings(port_10p0_1="not-a-port")
        with pytest.raises(ValueError):
            configured_modbus_ports(settings, [_spec("10P0.1")])


class TestResolveBridgeEndpoints:
    def test_resolves_host_and_default_port(self):
        settings = _settings(host_10p0_1="192.168.0.10")
        endpoints = resolve_bridge_endpoints(
            settings, [_spec("10P0.1")], default_port=502
        )
        assert endpoints[0].host == "192.168.0.10"
        assert endpoints[0].port == 502
        assert endpoints[0].spec.panel == "10P0.1"

    def test_panel_port_overrides_default(self):
        settings = _settings(host_10p0_1="192.168.0.10", port_10p0_1="1502")
        endpoints = resolve_bridge_endpoints(
            settings, [_spec("10P0.1")], default_port=502
        )
        assert endpoints[0].port == 1502

    def test_unconfigured_panels_are_skipped(self):
        settings = _settings(host_10p0_1="192.168.0.10")
        endpoints = resolve_bridge_endpoints(
            settings, [_spec("10P0.1"), _spec("10P1")], default_port=502
        )
        assert [e.spec.panel for e in endpoints] == ["10P0.1"]

    def test_no_configured_panels_raises(self):
        with pytest.raises(ValueError, match="No Modbus gateway hosts"):
            resolve_bridge_endpoints(
                _settings(), [_spec("10P0.1"), _spec("10P1")], default_port=502
            )

    def test_empty_host_counts_as_unconfigured(self):
        settings = _settings(host_10p0_1="")
        with pytest.raises(ValueError, match="No Modbus gateway hosts"):
            resolve_bridge_endpoints(settings, [_spec("10P0.1")], default_port=502)


class TestConfiguredSpecs:
    def test_keeps_only_panels_with_a_host(self):
        settings = _settings(host_10p1="192.168.0.10")
        specs = [_spec("10P0.1"), _spec("10P1")]
        assert [spec.panel for spec in configured_specs(settings, specs)] == ["10P1"]

    def test_stub_serves_only_configured_ports(self):
        # Partial rollout: only 10P1 is deployed, pinned to stub port 15021.
        # The stub must not also spread the undeployed 10P0.3 onto 15021.
        settings = _settings(host_10p1="stub", port_10p1="15021")
        specs = [_spec("10P0.1"), _spec("10P0.3"), _spec("10P1")]
        served = configured_specs(settings, specs) or specs
        assert stub_ports(settings, served, base_port=15020) == {"10P1": 15021}


class TestStubPorts:
    def test_unconfigured_panels_spread_from_base_port(self):
        specs = [_spec("10P0.1"), _spec("10P1")]
        assert stub_ports(_settings(), specs, base_port=5020) == {
            "10P0.1": 5020,
            "10P1": 5021,
        }

    def test_explicit_override_wins(self):
        settings = _settings(port_10p1="16000")
        specs = [_spec("10P0.1"), _spec("10P1")]
        assert stub_ports(settings, specs, base_port=5020) == {
            "10P0.1": 5020,
            "10P1": 16000,
        }
