from unittest.mock import patch

from pydantic_settings import CliApp

from zero_hull_temperature.cli import ZeroHullTemperature


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
