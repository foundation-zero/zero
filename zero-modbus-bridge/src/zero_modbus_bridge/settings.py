from pathlib import Path
from secrets import token_hex
from typing import Any

from faststream.mqtt import ReconnectConfig
from faststream.security import SASLPlaintext
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.server import ModbusServer

from zero_modbus_bridge.mqtt import ReportingBroker
from zero_modbus_bridge.readiness import Readiness

model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    env_nested_delimiter="__",
    env_prefix="",
    extra="ignore",
)


class MqttSettings(BaseSettings):
    model_config = model_config

    mqtt_host: str
    mqtt_port: int
    mqtt_username: str | None = None
    mqtt_password: str | None = None
    mqtt_client_id: str = Field(default_factory=lambda: f"modbus-bridge-{token_hex(4)}")
    # On the emptyDir the chart mounts at /tmp; its readiness probe reads it.
    readiness_file: Path = Path("/tmp/readiness")

    def make_broker(self, readiness: Readiness) -> ReportingBroker:
        kwargs: dict[str, Any] = {}
        if self.mqtt_username and self.mqtt_password:
            kwargs["security"] = SASLPlaintext(self.mqtt_username, self.mqtt_password)

        async def exit_on_give_up() -> None:
            readiness.exit("mqtt: client gave up reconnecting")

        return ReportingBroker(
            f"{self.mqtt_host}:{self.mqtt_port}",
            readiness,
            client_id=self.mqtt_client_id,
            # Retry for as long as it takes, and at most 30 s apart, so we are
            # back within about 30 s of the broker; the readiness deadline
            # bounds the total.
            reconnect=ReconnectConfig(max_attempts=None, max_delay=30.0),
            # 60 s races RabbitMQ's keepalive window.
            keepalive=15,
            on_connection_recovery_failed=exit_on_give_up,
            **kwargs,
        )


class ModbusSettings(BaseSettings):
    model_config = model_config

    modbus_host: str
    modbus_port: int
    modbus_probe_interval: int = 10

    def modbus_client(self) -> ModbusClient:
        return ModbusClient(self.modbus_host, self.modbus_port, auto_open=False)

    def modbus_server(self, data_handler=None) -> ModbusServer:
        return ModbusServer(
            self.modbus_host, self.modbus_port, no_block=True, data_hdl=data_handler
        )
