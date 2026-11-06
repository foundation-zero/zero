"""MQTT connection settings for the two brokers this service bridges.

Input: A+T's onboard MQTT broker (`ATPX_MQTT_*`), no auth.
Output: our own MQTT broker (`MQTT_*`), optionally authenticated.

Locally both resolve to the same `vernemq` container; in production
`ATPX_MQTT_HOST` points at A+T's real broker instead.
"""

from secrets import token_hex
from typing import Any

from faststream.mqtt import ReconnectConfig
from faststream.security import SASLPlaintext
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from zero_atpx_nmea.mqtt import ReportingBroker
from zero_atpx_nmea.readiness import Readiness

# Both are required: without input there is nothing to parse, without output
# nowhere to publish it. These names appear in the readiness status.
INPUT_BROKER = "atpx-mqtt"
OUTPUT_BROKER = "mqtt"

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
    atpx_mqtt_client_id: str = Field(
        default_factory=lambda: f"atpx-nmea-in-{token_hex(4)}"
    )

    def make_broker(self, readiness: Readiness) -> ReportingBroker:
        return _make_broker(
            f"{self.atpx_mqtt_host}:{self.atpx_mqtt_port}",
            readiness,
            INPUT_BROKER,
            client_id=self.atpx_mqtt_client_id,
        )


class OutputMqttSettings(BaseSettings):
    """Config for our own MQTT broker (output)."""

    model_config = model_config

    mqtt_host: str
    mqtt_port: int
    mqtt_user: str | None = None
    mqtt_password: str | None = None
    mqtt_client_id: str = Field(default_factory=lambda: f"atpx-nmea-out-{token_hex(4)}")

    def make_broker(self, readiness: Readiness) -> ReportingBroker:
        kwargs: dict[str, Any] = {"client_id": self.mqtt_client_id}
        if self.mqtt_user and self.mqtt_password:
            kwargs["security"] = SASLPlaintext(self.mqtt_user, self.mqtt_password)
        return _make_broker(
            f"{self.mqtt_host}:{self.mqtt_port}", readiness, OUTPUT_BROKER, **kwargs
        )


def _make_broker(
    url: str, readiness: Readiness, dependency: str, **kwargs: Any
) -> ReportingBroker:
    async def exit_on_give_up() -> None:
        readiness.exit(f"{dependency}: client gave up reconnecting")

    return ReportingBroker(
        url,
        readiness,
        dependency,
        # Retry for as long as it takes, and at most 30 s apart, so we are
        # back within about 30 s of the broker; the readiness deadline
        # bounds the total.
        reconnect=ReconnectConfig(max_attempts=None, max_delay=30.0),
        # 60 s races RabbitMQ's keepalive window.
        keepalive=15,
        on_connection_recovery_failed=exit_on_give_up,
        **kwargs,
    )
