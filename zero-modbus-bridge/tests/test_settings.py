import re
from unittest.mock import MagicMock

import pytest

from zero_modbus_bridge.mqtt import ReportingBroker
from zero_modbus_bridge.readiness import Readiness
from zero_modbus_bridge.settings import MqttSettings


@pytest.fixture(autouse=True)
def _mqtt_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_HOST", "localhost")
    monkeypatch.setenv("MQTT_PORT", "1883")
    monkeypatch.delenv("MQTT_CLIENT_ID", raising=False)


def test_mqtt_client_id_default():
    settings = MqttSettings(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(r"modbus-bridge-[0-9a-f]{8}", settings.mqtt_client_id)


def test_mqtt_client_id_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_CLIENT_ID", "custom-id")
    settings = MqttSettings(_env_file=None)  # type: ignore[call-arg]
    assert settings.mqtt_client_id == "custom-id"


def test_make_broker_reconnects_indefinitely_and_quickly(
    monkeypatch: pytest.MonkeyPatch,
):
    broker = MagicMock()
    monkeypatch.setattr("zero_modbus_bridge.settings.ReportingBroker", broker)
    MqttSettings(_env_file=None).make_broker(Readiness(None, {"mqtt": "connecting"}))  # type: ignore[call-arg]

    options = broker.call_args.kwargs
    assert options["reconnect"].max_attempts is None
    assert options["reconnect"].max_delay == 30
    assert options["keepalive"] == 15


async def test_make_broker_exits_when_client_gives_up(
    monkeypatch: pytest.MonkeyPatch,
):
    broker = MagicMock()
    monkeypatch.setattr("zero_modbus_bridge.settings.ReportingBroker", broker)
    readiness = MagicMock(spec=Readiness)
    MqttSettings(_env_file=None).make_broker(readiness)  # type: ignore[call-arg]

    await broker.call_args.kwargs["on_connection_recovery_failed"]()
    readiness.exit.assert_called_once_with("mqtt: client gave up reconnecting")


def test_make_broker_builds_a_real_broker():
    settings = MqttSettings(_env_file=None, mqtt_username="u", mqtt_password="p")  # type: ignore[call-arg]
    assert isinstance(
        settings.make_broker(Readiness(None, {"mqtt": "connecting"})), ReportingBroker
    )
