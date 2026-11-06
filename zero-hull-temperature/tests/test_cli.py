import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic_settings import CliApp
from zero_modbus_bridge.readiness import Readiness
from zero_modbus_bridge.settings import MqttSettings

from zero_hull_temperature.cli import (
    ReadWithMqttCmd,
    RunCmd,
    StubCmd,
    ZeroHullTemperature,
)


def test_read_mqtt_no_skip():
    with patch("zero_hull_temperature.cli.ReadWithMqttCmd.cli_cmd") as mock_run_command:
        CliApp.run(
            ZeroHullTemperature,
            [
                "read-with-mqtt",
                "--modbus-host",
                "localhost",
                "--modbus-port",
                "502",
                "--mqtt-host",
                "localhost",
                "--mqtt-port",
                "1883",
            ],
            cli_exit_on_error=False,
        )
        mock_run_command.assert_called_once()


def test_read_mqtt_skip():
    with patch("zero_hull_temperature.cli.ReadSkipMqttCmd.cli_cmd") as mock_run_command:
        CliApp.run(
            ZeroHullTemperature,
            [
                "read-skip-mqtt",
                "--modbus-host",
                "localhost",
                "--modbus-port",
                "502",
            ],
            cli_exit_on_error=False,
        )
        mock_run_command.assert_called_once()


def test_asyncapi_payload_declares_timestamp():
    from zero_hull_temperature.cli import build_asyncapi

    schemas = build_asyncapi()["components"]["schemas"]
    assert "TimeStamp" in schemas["HullTemperature"]["properties"]


def test_buffer_size_covers_five_minutes():
    from zero_hull_temperature.bridge_relay import buffer_size_for

    assert buffer_size_for(probe_interval=10, topic_count=1) == 30


@pytest.fixture
def required_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MODBUS_HOST", "localhost")
    monkeypatch.setenv("MODBUS_PORT", "502")
    monkeypatch.setenv("MQTT_HOST", "localhost")
    monkeypatch.setenv("MQTT_PORT", "1883")
    monkeypatch.delenv("MQTT_CLIENT_ID", raising=False)


def test_read_with_mqtt_default_client_id(required_env):
    cmd = ReadWithMqttCmd(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(r"hull-temperature-[0-9a-f]{8}", cmd.mqtt_client_id)


def test_read_with_mqtt_client_id_from_env(required_env, monkeypatch):
    monkeypatch.setenv("MQTT_CLIENT_ID", "custom-id")
    cmd = ReadWithMqttCmd(_env_file=None)  # type: ignore[call-arg]
    assert cmd.mqtt_client_id == "custom-id"


def test_run_default_client_id(required_env):
    cmd = RunCmd(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(r"hull-temperature-[0-9a-f]{8}", cmd.mqtt_client_id)


def test_run_client_id_from_env(required_env, monkeypatch):
    monkeypatch.setenv("MQTT_CLIENT_ID", "custom-id")
    cmd = RunCmd(_env_file=None)  # type: ignore[call-arg]
    assert cmd.mqtt_client_id == "custom-id"


def test_stub_default_client_id(required_env):
    cmd = StubCmd(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(r"hull-temperature-stub-[0-9a-f]{8}", cmd.mqtt_client_id)


def test_stub_client_id_from_env(required_env, monkeypatch):
    monkeypatch.setenv("MQTT_CLIENT_ID", "custom-id")
    cmd = StubCmd(_env_file=None)  # type: ignore[call-arg]
    assert cmd.mqtt_client_id == "custom-id"


@pytest.fixture
def make_broker(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    make_broker = MagicMock()
    monkeypatch.setattr(MqttSettings, "make_broker", make_broker)
    return make_broker


@pytest.fixture
def from_settings(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    from_settings = MagicMock()
    from_settings.return_value.run_once = AsyncMock()
    monkeypatch.setattr(
        "zero_hull_temperature.cli.RelaySwitchingBridge.from_settings", from_settings
    )
    return from_settings


async def test_run_makes_the_gateway_count_for_readiness(
    required_env, monkeypatch, make_broker: MagicMock, from_settings: MagicMock
):
    app = MagicMock()
    app.return_value.run = AsyncMock()
    monkeypatch.setattr("zero_hull_temperature.cli.FastStream", app)

    await RunCmd(_env_file=None).cli_cmd()  # type: ignore[call-arg]

    readiness = make_broker.call_args.args[0]
    assert isinstance(readiness, Readiness)
    assert from_settings.call_args.kwargs["readiness"] is readiness


async def test_read_with_mqtt_reads_once(
    required_env, make_broker: MagicMock, from_settings: MagicMock
):
    await ReadWithMqttCmd(_env_file=None).cli_cmd()  # type: ignore[call-arg]

    from_settings.return_value.run_once.assert_awaited_once()
