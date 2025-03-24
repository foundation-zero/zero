import os
from unittest import mock

from io_processing.config import MQTTConfig


@mock.patch.dict(
    os.environ, {"MQTT_HOST": "example.com", "MQTT_PORT": "1884"}, clear=True
)
def test_mqtt_config_not_default():
    config = MQTTConfig()  # pyright: ignore
    assert config.model_dump() == {"host": "example.com", "port": 1884}
