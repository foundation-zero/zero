import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zero_atpx_nmea.mqtt import ReportingBroker
from zero_atpx_nmea.readiness import Readiness
from zero_atpx_nmea.settings import (
    INPUT_BROKER,
    OUTPUT_BROKER,
    InputMqttSettings,
    OutputMqttSettings,
)


@pytest.fixture(autouse=True)
def _mqtt_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ATPX_MQTT_HOST", "localhost")
    monkeypatch.setenv("ATPX_MQTT_PORT", "1883")
    monkeypatch.setenv("MQTT_HOST", "localhost")
    monkeypatch.setenv("MQTT_PORT", "1883")
    monkeypatch.delenv("ATPX_MQTT_CLIENT_ID", raising=False)
    monkeypatch.delenv("MQTT_CLIENT_ID", raising=False)


def test_input_client_id_default():
    settings = InputMqttSettings(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(r"atpx-nmea-in-[0-9a-f]{8}", settings.atpx_mqtt_client_id)


def test_input_client_id_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ATPX_MQTT_CLIENT_ID", "custom-in")
    settings = InputMqttSettings(_env_file=None)  # type: ignore[call-arg]
    assert settings.atpx_mqtt_client_id == "custom-in"


def test_output_client_id_default():
    settings = OutputMqttSettings(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(r"atpx-nmea-out-[0-9a-f]{8}", settings.mqtt_client_id)


def test_output_client_id_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_CLIENT_ID", "custom-out")
    settings = OutputMqttSettings(_env_file=None)  # type: ignore[call-arg]
    assert settings.mqtt_client_id == "custom-out"


@pytest.fixture
def readiness(tmp_path: Path) -> Readiness:
    return Readiness(tmp_path / "ready", [INPUT_BROKER, OUTPUT_BROKER])


@pytest.mark.parametrize(
    ("settings", "dependency"),
    [(InputMqttSettings, INPUT_BROKER), (OutputMqttSettings, OUTPUT_BROKER)],
)
def test_make_broker_reconnects_indefinitely_and_quickly(
    monkeypatch: pytest.MonkeyPatch,
    readiness: Readiness,
    settings: type[InputMqttSettings | OutputMqttSettings],
    dependency: str,
):
    broker = MagicMock()
    monkeypatch.setattr("zero_atpx_nmea.settings.ReportingBroker", broker)
    settings(_env_file=None).make_broker(readiness)  # type: ignore[call-arg]

    assert broker.call_args.args[2] == dependency
    options = broker.call_args.kwargs
    assert options["reconnect"].max_attempts is None
    assert options["reconnect"].max_delay == 30
    assert options["keepalive"] == 15


async def test_make_broker_exits_when_client_gives_up(monkeypatch: pytest.MonkeyPatch):
    broker = MagicMock()
    monkeypatch.setattr("zero_atpx_nmea.settings.ReportingBroker", broker)
    readiness = MagicMock(spec=Readiness)
    InputMqttSettings(_env_file=None).make_broker(readiness)  # type: ignore[call-arg]

    await broker.call_args.kwargs["on_connection_recovery_failed"]()
    readiness.exit.assert_called_once_with("atpx-mqtt: client gave up reconnecting")


def test_make_broker_builds_real_brokers(readiness: Readiness):
    output = OutputMqttSettings(_env_file=None, mqtt_user="u", mqtt_password="p")  # type: ignore[call-arg]
    assert isinstance(output.make_broker(readiness), ReportingBroker)
    input_ = InputMqttSettings(_env_file=None)  # type: ignore[call-arg]
    assert isinstance(input_.make_broker(readiness), ReportingBroker)
