import re

import pytest
from pydantic_settings import BaseSettings

from zero_atpx_nmea.mqtt import RecoveringBroker
from zero_atpx_nmea.settings import InputMqttSettings, OutputMqttSettings


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


@pytest.mark.parametrize(
    ("settings", "name"),
    [(InputMqttSettings, "atpx-mqtt"), (OutputMqttSettings, "mqtt")],
)
def test_brokers_ride_out_outages(settings: type[BaseSettings], name: str):
    broker = settings(_env_file=None).make_broker()  # type: ignore[call-arg]
    kwargs = broker._connection_kwargs
    assert isinstance(broker, RecoveringBroker)
    assert broker._name == name
    assert kwargs["reconnect"].max_attempts is None
    assert kwargs["reconnect"].max_delay == 30.0
    assert kwargs["keepalive"] == 15
