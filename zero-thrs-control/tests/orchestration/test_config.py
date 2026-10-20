import re

import pytest

from thrs.orchestration.config import Config


@pytest.fixture(autouse=True)
def _required_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_HOST", "localhost")
    monkeypatch.setenv("MQTT_PORT", "1883")
    monkeypatch.setenv("MQTT_DEVICES_TOPIC_PREFIX", "devices")
    monkeypatch.setenv("MQTT_CONTROLLER_TOPIC_PREFIX", "controller")
    monkeypatch.setenv("MQTT_CONTROLLER_TOPIC_SUFFIX", "set")
    monkeypatch.setenv("MQTT_SIMULATOR_TOPIC_PREFIX", "simulator")
    monkeypatch.setenv("MQTT_SIMULATOR_TOPIC_SUFFIX", "set")
    monkeypatch.setenv("MQTT_CONTROL_TOPIC_SUFFIX", "control")
    for name in ("API", "CONTROL", "SIMULATION", "LOCKSTEP"):
        monkeypatch.delenv(f"MQTT_{name}_CLIENT_ID", raising=False)


def test_mqtt_api_client_id_default():
    config = Config(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(r"thrs-api-[0-9a-f]{8}", config.mqtt_api_client_id)


def test_mqtt_api_client_id_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_API_CLIENT_ID", "custom-id")
    config = Config(_env_file=None)  # type: ignore[call-arg]
    assert config.mqtt_api_client_id == "custom-id"


def test_mqtt_control_client_id_default():
    config = Config(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(r"thrs-control-[0-9a-f]{8}", config.mqtt_control_client_id)


def test_mqtt_control_client_id_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_CONTROL_CLIENT_ID", "custom-id")
    config = Config(_env_file=None)  # type: ignore[call-arg]
    assert config.mqtt_control_client_id == "custom-id"


def test_mqtt_simulation_client_id_default():
    config = Config(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(
        r"thrs-simulation-[0-9a-f]{8}", config.mqtt_simulation_client_id
    )


def test_mqtt_simulation_client_id_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_SIMULATION_CLIENT_ID", "custom-id")
    config = Config(_env_file=None)  # type: ignore[call-arg]
    assert config.mqtt_simulation_client_id == "custom-id"


def test_mqtt_lockstep_client_id_default():
    config = Config(_env_file=None)  # type: ignore[call-arg]
    assert re.fullmatch(r"thrs-lockstep-[0-9a-f]{8}", config.mqtt_lockstep_client_id)


def test_mqtt_lockstep_client_id_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_LOCKSTEP_CLIENT_ID", "custom-id")
    config = Config(_env_file=None)  # type: ignore[call-arg]
    assert config.mqtt_lockstep_client_id == "custom-id"
