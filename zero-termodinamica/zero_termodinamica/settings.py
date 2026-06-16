from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiomqtt import Client as MqttClient
from pydantic import BaseModel
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.server import ModbusServer


class MqttSettings(BaseModel):
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


class ModbusSettings(BaseModel):
    modbus_host: str
    modbus_port: int

    def modbus_client(self):
        return ModbusClient(self.modbus_host, self.modbus_port)

    def modbus_server(self):
        return ModbusServer(self.modbus_host, self.modbus_port, no_block=True)
