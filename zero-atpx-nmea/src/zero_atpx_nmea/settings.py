"""MQTT connection settings for the two brokers this service bridges.

Input: A+T's onboard MQTT broker (`ATPX_MQTT_*`), no auth.
Output: our own MQTT broker (`MQTT_*`), optionally authenticated.

Locally both resolve to the same `vernemq` container; in production
`ATPX_MQTT_HOST` points at A+T's real broker instead.
"""

from secrets import token_hex

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from zero_mqtt import MqttSettings


class InputMqttSettings(MqttSettings):
    model_config = SettingsConfigDict(env_prefix="ATPX_")

    mqtt_client_id: str = Field(default_factory=lambda: f"atpx-nmea-in-{token_hex(4)}")


class OutputMqttSettings(MqttSettings):
    mqtt_client_id: str = Field(default_factory=lambda: f"atpx-nmea-out-{token_hex(4)}")
