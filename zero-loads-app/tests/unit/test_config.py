import re

import pytest

from loads.config import Settings


@pytest.fixture(autouse=True)
def _required_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PG_HOST", "localhost")
    monkeypatch.setenv("PG_PORT", "5432")
    monkeypatch.setenv("PG_USER", "user")
    monkeypatch.setenv("PG_PASSWORD", "password")
    monkeypatch.setenv("PG_DB", "db")
    monkeypatch.setenv("MQTT_HOST", "localhost")
    monkeypatch.setenv("MQTT_PORT", "1883")
    for name in ("API", "CONTROL", "STUB"):
        monkeypatch.delenv(f"MQTT_{name}_CLIENT_ID", raising=False)


def test_mqtt_api_client_id_default():
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(r"loads-api-[0-9a-f]{8}", settings.mqtt_api_client_id)


def test_mqtt_api_client_id_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_API_CLIENT_ID", "custom-id")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.mqtt_api_client_id == "custom-id"


def test_mqtt_control_client_id_default():
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(r"loads-control-[0-9a-f]{8}", settings.mqtt_control_client_id)


def test_mqtt_control_client_id_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_CONTROL_CLIENT_ID", "custom-id")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.mqtt_control_client_id == "custom-id"


def test_mqtt_stub_client_id_default():
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(r"loads-stub-[0-9a-f]{8}", settings.mqtt_stub_client_id)


def test_mqtt_stub_client_id_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_STUB_CLIENT_ID", "custom-id")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.mqtt_stub_client_id == "custom-id"
