import os
from unittest.mock import patch

from pydantic_settings import CliApp

from zero_termodinamica.cli import ZeroTermodinamica


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
                cli_exit_on_error=False,
            )

            mock_run_command.assert_called_once()
            instance = mock_run_command.call_args.args[0]
            assert instance.modbus_host == "127.0.0.1"
            assert instance.modbus_port == 502
            assert instance.mqtt_host == "localhost"
            assert instance.mqtt_port == 1883

    finally:
        # Cleanup
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
    os.environ["DEFAULT_VALUE"] = "42"

    try:
        with patch("zero_termodinamica.cli.StubCmd.cli_cmd") as mock_stub_command:
            CliApp.run(
                ZeroTermodinamica,
                ["stub"],
                cli_exit_on_error=False,
            )

            mock_stub_command.assert_called_once()
            instance = mock_stub_command.call_args.args[0]
            assert instance.modbus_host == "127.0.0.1"
            assert instance.modbus_port == 502
            assert instance.default_value == 42

    finally:
        # Cleanup
        for key in ["MODBUS_HOST", "MODBUS_PORT", "DEFAULT_VALUE"]:
            if key in os.environ:
                del os.environ[key]


def test_stub_cmd_from_args():
    """Test that ZeroTermodinamica.stub calls StubCmd.cli_cmd with expected arguments."""
    with patch("zero_termodinamica.cli.StubCmd.cli_cmd") as mock_stub_command:
        CliApp.run(
            ZeroTermodinamica,
            [
                "stub",
                "--modbus-host",
                "10.0.0.1",
                "--modbus-port",
                "503",
                "--default-value",
                "100",
            ],
            cli_exit_on_error=False,
        )

        mock_stub_command.assert_called_once()
        instance = mock_stub_command.call_args.args[0]
        assert instance.modbus_host == "10.0.0.1"
        assert instance.modbus_port == 503
        assert instance.default_value == 100


def test_run_cmd_from_args():
    """Test that ZeroTermodinamica.run calls RunCmd.cli_cmd with expected arguments."""
    with patch("zero_termodinamica.cli.RunCmd.cli_cmd") as mock_run_command:
        CliApp.run(
            ZeroTermodinamica,
            [
                "run",
                "--modbus-host",
                "10.0.0.1",
                "--modbus-port",
                "503",
                "--mqtt-host",
                "mqtt.local",
                "--mqtt-port",
                "1884",
            ],
            cli_exit_on_error=False,
        )
        mock_run_command.assert_called_once()
        instance = mock_run_command.call_args.args[0]
        assert instance.modbus_host == "10.0.0.1"
        assert instance.modbus_port == 503


def test_run_rtu_cmd_from_args():
    """Test that ZeroTermodinamica.run-rtu calls RunRTUCmd.cli_cmd with expected arguments."""
    with patch("zero_termodinamica.cli.RunRTUCmd.cli_cmd") as mock_run_rtu_command:
        CliApp.run(
            ZeroTermodinamica,
            [
                "run-rtu",
                "--modbus-serial-port",
                "/dev/ttyUSB0",
                "--baudrate",
                "9600",
                "--mqtt-host",
                "mqtt.local",
                "--mqtt-port",
                "1884",
            ],
            cli_exit_on_error=False,
        )

        mock_run_rtu_command.assert_called_once()
        instance = mock_run_rtu_command.call_args.args[0]
        assert instance.modbus_serial_port == "/dev/ttyUSB0"
        assert instance.baudrate == 9600


def test_run_rtu_cmd_from_env():
    """Test that ZeroTermodinamica run-rtu command picks up settings from env."""
    os.environ["MODBUS_SERIAL_PORT"] = "/dev/ttyUSB0"
    os.environ["BAUDRATE"] = "9600"
    os.environ["MQTT_HOST"] = "localhost"
    os.environ["MQTT_PORT"] = "1883"

    try:
        with patch("zero_termodinamica.cli.RunRTUCmd.cli_cmd") as mock_run_rtu_command:
            CliApp.run(
                ZeroTermodinamica,
                ["run-rtu"],
                cli_exit_on_error=False,
            )

            mock_run_rtu_command.assert_called_once()
            instance = mock_run_rtu_command.call_args.args[0]
            assert instance.modbus_serial_port == "/dev/ttyUSB0"
            assert instance.baudrate == 9600
            assert instance.mqtt_host == "localhost"
            assert instance.mqtt_port == 1883

    finally:
        # Cleanup
        for key in ["MODBUS_SERIAL_PORT", "BAUDRATE", "MQTT_HOST", "MQTT_PORT"]:
            if key in os.environ:
                del os.environ[key]
