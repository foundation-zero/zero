import re

import pytest

from zero_atpx_nmea.settings import InputMqttSettings, OutputMqttSettings


@pytest.fixture(autouse=True)
def _mqtt_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ATPX_MQTT_HOST", "atpx-broker")
    monkeypatch.setenv("ATPX_MQTT_PORT", "1884")
    monkeypatch.setenv("MQTT_HOST", "our-broker")
    monkeypatch.setenv("MQTT_PORT", "1883")
    monkeypatch.setenv("MQTT_USERNAME", "user")
    monkeypatch.delenv("ATPX_MQTT_CLIENT_ID", raising=False)
    monkeypatch.delenv("MQTT_CLIENT_ID", raising=False)


def test_input_reads_the_atpx_variables():
    settings = InputMqttSettings(_env_file=None)  # type: ignore[call-arg]
    assert (settings.mqtt_host, settings.mqtt_port) == ("atpx-broker", 1884)
    assert settings.mqtt_username is None
    assert re.fullmatch(r"atpx-nmea-in-[0-9a-f]{8}", settings.mqtt_client_id)


def test_output_reads_the_mqtt_variables():
    settings = OutputMqttSettings(_env_file=None)  # type: ignore[call-arg]
    assert (settings.mqtt_host, settings.mqtt_port) == ("our-broker", 1883)
    assert settings.mqtt_username == "user"
    assert re.fullmatch(r"atpx-nmea-out-[0-9a-f]{8}", settings.mqtt_client_id)


def test_client_ids_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ATPX_MQTT_CLIENT_ID", "custom-in")
    monkeypatch.setenv("MQTT_CLIENT_ID", "custom-out")
    assert InputMqttSettings(_env_file=None).mqtt_client_id == "custom-in"  # type: ignore[call-arg]
    assert OutputMqttSettings(_env_file=None).mqtt_client_id == "custom-out"  # type: ignore[call-arg]
