import os
from unittest.mock import patch

from pydantic_settings import CliApp

from zero_termodinamica.cli import RunCmd, StubCmd, ZeroTermodinamica


def test_run_cmd_from_env():
    """Test that ZeroTermodinamica run command picks up settings from env and calls the subcommand."""
    os.environ["MODBUS_HOST"] = "127.0.0.1"
    os.environ["MODBUS_PORT"] = "502"
    os.environ["MQTT_HOST"] = "localhost"
    os.environ["MQTT_PORT"] = "1883"

    try:
        with patch("zero_termodinamica.cli.RunCmd.cli_cmd") as mock_run_command:
            CliApp.run(
                ZeroTermodinamica,
                ["run"],
            )
            instance = mock_run_command.call_args[0][0]
            assert instance.modbus_host == "127.0.0.1"
            assert instance.mqtt_port == 1883
    finally:
        for key in [
            "MODBUS_HOST",
            "MODBUS_PORT",
            "MQTT_HOST",
            "MQTT_PORT",
        ]:
            if key in os.environ:
                del os.environ[key]


def test_stub_cmd_from_env():
    """Test that ZeroTermodinamica stub command picks up settings from env and calls the subcommand."""
    os.environ["MODBUS_HOST"] = "127.0.0.1"
    os.environ["MODBUS_PORT"] = "502"
    os.environ["DEFAULT_REGISTER_VALUE"] = "42"

    try:
        with patch("zero_termodinamica.cli.StubCmd.cli_cmd") as mock_stub_command:
            CliApp.run(
                ZeroTermodinamica,
                ["stub"],
            )
            assert mock_stub_command.call_count == 1
            instance = mock_stub_command.call_args[0][0]
            assert instance.modbus_host == "127.0.0.1"
            assert instance.modbus_port == 502
            assert instance.default_register_value == 42
    finally:
        for key in ["MODBUS_HOST", "MODBUS_PORT", "DEFAULT_REGISTER_VALUE"]:
            if key in os.environ:
                del os.environ[key]


def test_stub_cmd_from_args():
    """Test that ZeroTermodinamica.stub calls StubCmd.cli_cmd with expected arguments."""
    with patch("zero_termodinamica.cli.StubCmd.cli_cmd") as mock_stub_command:
        CliApp.run(
            ZeroTermodinamica,
            [
                "stub",
                "--modbus-host=192.168.1.1",
                "--modbus-port=1502",
                "--default-register-value=100",
            ],
        )
        assert mock_stub_command.call_count == 1
        stub_cmd: StubCmd = mock_stub_command.call_args[0][0]
        assert stub_cmd.modbus_host == "192.168.1.1"
        assert stub_cmd.modbus_port == 1502
        assert stub_cmd.default_register_value == 100


def test_run_cmd_from_args():
    """Test that ZeroTermodinamica.run calls RunCmd.cli_cmd with expected arguments."""
    with patch("zero_termodinamica.cli.RunCmd.cli_cmd") as mock_run_command:
        CliApp.run(
            ZeroTermodinamica,
            [
                "run",
                "--modbus-host=192.168.1.1",
                "--modbus-port=1502",
                "--mqtt-host=localhost",
                "--mqtt-port=1884",
            ],
        )
        assert mock_run_command.call_count == 1
        run_cmd: RunCmd = mock_run_command.call_args[0][0]
        assert run_cmd.modbus_host == "192.168.1.1"
        assert run_cmd.modbus_port == 1502
        assert run_cmd.mqtt_host == "localhost"
        assert run_cmd.mqtt_port == 1884
