import re

import pytest

from zero_termodinamica.cli import RunCmd


def test_run_cmd_settings_from_env(required_env):
    """Test that RunCmd correctly picks up settings from environment variables without any prefix."""
    settings = RunCmd()
    assert settings.modbus_host == "127.0.0.1"
    assert settings.modbus_port == 502
    assert settings.mqtt_host == "localhost"
    assert settings.mqtt_port == 1883


@pytest.fixture
def required_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MODBUS_HOST", "127.0.0.1")
    monkeypatch.setenv("MODBUS_PORT", "502")
    monkeypatch.setenv("MQTT_HOST", "localhost")
    monkeypatch.setenv("MQTT_PORT", "1883")
    monkeypatch.delenv("MQTT_CLIENT_ID", raising=False)


def test_run_cmd_default_client_id(required_env):
    assert re.fullmatch(r"termodinamica-[0-9a-f]{8}", RunCmd().mqtt_client_id)


def test_run_cmd_client_id_from_env(required_env, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_CLIENT_ID", "custom-id")
    assert RunCmd().mqtt_client_id == "custom-id"
