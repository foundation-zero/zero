import os
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic_settings import CliApp
from zero_modbus_bridge.readiness import Readiness

from zero_termodinamica.cli import RunCmd, StubCmd, ZeroTermodinamica
from zero_termodinamica.io import read_modbus_topics


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


def test_stub_cmd_serves_termodinamica_topics():
    """Test that StubCmd.cli_cmd starts a stub serving the termodinamica topics."""
    stub_cmd = StubCmd(
        modbus_host="127.0.0.1", modbus_port=502, default_register_value=7
    )

    with patch("zero_termodinamica.cli.Stub") as mock_stub:
        stub_cmd.cli_cmd()

    settings, topics, default_value = mock_stub.from_settings.call_args.args
    assert settings is stub_cmd
    assert [topic.topic for topic in topics] == [
        topic.topic for topic in read_modbus_topics()
    ]
    assert default_value == 7
    mock_stub.from_settings.return_value.run.assert_called_once_with()


async def test_run_makes_the_gateway_count_for_readiness(monkeypatch):
    make_broker = MagicMock()
    from_settings = MagicMock()
    app = MagicMock()
    app.return_value.run = AsyncMock()
    monkeypatch.setattr(RunCmd, "make_broker", make_broker)
    monkeypatch.setattr(
        "zero_termodinamica.cli.ModbusBridge.from_settings", from_settings
    )
    monkeypatch.setattr("zero_termodinamica.cli.FastStream", app)
    monkeypatch.setenv("MODBUS_HOST", "gateway")
    monkeypatch.setenv("MODBUS_PORT", "502")
    monkeypatch.setenv("MQTT_HOST", "broker")
    monkeypatch.setenv("MQTT_PORT", "1883")

    await RunCmd().cli_cmd()  # pyright: ignore

    readiness = make_broker.call_args.args[0]
    assert isinstance(readiness, Readiness)
    assert from_settings.call_args.kwargs["readiness"] is readiness
