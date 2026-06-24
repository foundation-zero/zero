from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiomqtt import Client as MqttClient
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
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

    @asynccontextmanager
    async def mqtt_client(self) -> AsyncGenerator[MqttClient, None]:
        async with MqttClient(
            self.mqtt_host,
            self.mqtt_port,
            username=self.mqtt_username,
            password=self.mqtt_password,
        ) as mqtt:
            yield mqtt


class ModbusSettings(BaseSettings):
    model_config = model_config

    modbus_host: str
    modbus_port: int
    modbus_probe_interval: int = 10

    def modbus_client(self):
        return ModbusClient(self.modbus_host, self.modbus_port, auto_open=False)

    def modbus_server(self, data_handler):
        return ModbusServer(
            self.modbus_host, self.modbus_port, no_block=True, data_hdl=data_handler
        )
