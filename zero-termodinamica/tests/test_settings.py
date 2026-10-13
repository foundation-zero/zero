import os
import re

import pytest

from zero_termodinamica.cli import RunCmd


def test_run_cmd_settings_from_env():
    """Test that RunCmd correctly picks up settings from environment variables without any prefix."""
    os.environ["MODBUS_HOST"] = "127.0.0.1"
    os.environ["MODBUS_PORT"] = "502"
    os.environ["MQTT_HOST"] = "localhost"
    os.environ["MQTT_PORT"] = "1883"

    try:
        settings = RunCmd()  # pyright: ignore
        assert settings.modbus_host == "127.0.0.1"
        assert settings.modbus_port == 502
        assert settings.mqtt_host == "localhost"
        assert settings.mqtt_port == 1883
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


@pytest.fixture
def required_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MODBUS_HOST", "127.0.0.1")
    monkeypatch.setenv("MODBUS_PORT", "502")
    monkeypatch.setenv("MQTT_HOST", "localhost")
    monkeypatch.setenv("MQTT_PORT", "1883")
    monkeypatch.delenv("MQTT_CLIENT_ID", raising=False)


def test_run_cmd_default_client_id(required_env):
    assert re.fullmatch(r"termodinamica-[0-9a-f]{8}", RunCmd().mqtt_client_id)  # pyright: ignore


def test_run_cmd_client_id_from_env(required_env, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_CLIENT_ID", "custom-id")
    assert RunCmd().mqtt_client_id == "custom-id"  # pyright: ignore
