from contextlib import asynccontextmanager

import pytest

from zero_atpx_nmea import cli
from zero_atpx_nmea.cli import RunCmd


class _FakeApp:
    async def run(self):
        pass


class _FakeHealth:
    def __init__(self, checks):
        self.checks = checks

    @asynccontextmanager
    async def serve(self):
        yield


def _fake_build_app(input_broker, output_broker):
    return _FakeApp()


async def test_run_cmd_is_ready_on_both_brokers(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ATPX_MQTT_HOST", "atpx-broker")
    monkeypatch.setenv("ATPX_MQTT_PORT", "1883")
    monkeypatch.setenv("MQTT_HOST", "our-broker")
    monkeypatch.setenv("MQTT_PORT", "1883")
    healths: list[_FakeHealth] = []

    def fake_health(_settings, checks):
        healths.append(_FakeHealth(checks))
        return healths[-1]

    monkeypatch.setattr(cli, "build_app", _fake_build_app)
    monkeypatch.setattr(cli, "Health", fake_health)

    await RunCmd().cli_cmd()

    assert sorted(healths[0].checks) == ["mqtt-input", "mqtt-output"]
