from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pydantic import BaseModel
from aiomqtt import Client as MqttClient

from zero_hull_temperature.addresses import PATH, TOPIC

from pyModbusTCP.server import ModbusServer
from pyModbusTCP.client import ModbusClient


class MqttSettings(BaseModel):
    mqtt_host: str
    mqtt_port: int
    mqtt_topic: str = TOPIC
    json_path: str = PATH

    @asynccontextmanager
    async def mqtt_client(self) -> AsyncGenerator[MqttClient, None]:
        async with MqttClient(self.mqtt_host, self.mqtt_port) as mqtt:
            yield mqtt


class ModbusSettings(BaseModel):
    modbus_host: str
    modbus_port: int

    def modbus_client(self):
        return ModbusClient(self.modbus_host, self.modbus_port)

    def modbus_server(self):
        return ModbusServer(self.modbus_host, self.modbus_port, no_block=True)
