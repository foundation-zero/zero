"""MQTT connection settings for the two brokers this service bridges.

Input: A+T's onboard MQTT broker (`ATPX_MQTT_*`), no auth.
Output: our own MQTT broker (`MQTT_*`), optionally authenticated.

Locally both resolve to the same `vernemq` container; in production
`ATPX_MQTT_HOST` points at A+T's real broker instead.
"""

from typing import Any

from faststream.mqtt import MQTTBroker
from faststream.security import SASLPlaintext
from pydantic_settings import BaseSettings, SettingsConfigDict

model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="allow",
    env_nested_delimiter="__",
)


class InputMqttSettings(BaseSettings):
    """Config for A+T's onboard MQTT broker (input, no auth)."""

    model_config = model_config

    atpx_mqtt_host: str
    atpx_mqtt_port: int

    def make_broker(self) -> MQTTBroker:
        return MQTTBroker(f"{self.atpx_mqtt_host}:{self.atpx_mqtt_port}")


class OutputMqttSettings(BaseSettings):
    """Config for our own MQTT broker (output)."""

    model_config = model_config

    mqtt_host: str
    mqtt_port: int
    mqtt_user: str | None = None
    mqtt_password: str | None = None

    def make_broker(self) -> MQTTBroker:
        kwargs: dict[str, Any] = {}
        if self.mqtt_user and self.mqtt_password:
            kwargs["security"] = SASLPlaintext(self.mqtt_user, self.mqtt_password)
        return MQTTBroker(f"{self.mqtt_host}:{self.mqtt_port}", **kwargs)
