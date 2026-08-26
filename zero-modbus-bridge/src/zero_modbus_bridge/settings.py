from typing import Any

from faststream.mqtt import MQTTBroker
from faststream.security import SASLPlaintext
from pydantic_settings import BaseSettings, SettingsConfigDict
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.server import ModbusServer

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

    def make_broker(self) -> MQTTBroker:
        kwargs: dict[str, Any] = {}
        if self.mqtt_username and self.mqtt_password:
            kwargs["security"] = SASLPlaintext(self.mqtt_username, self.mqtt_password)
        return MQTTBroker(f"{self.mqtt_host}:{self.mqtt_port}", **kwargs)


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
