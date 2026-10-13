import re
from unittest.mock import patch

import pytest
from pydantic_settings import CliApp

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
