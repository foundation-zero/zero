import re

import pytest

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
