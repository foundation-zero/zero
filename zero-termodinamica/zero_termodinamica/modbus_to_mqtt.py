import asyncio
import json
import logging
from asyncio import TaskGroup
from contextlib import asynccontextmanager
from itertools import groupby
from typing import AsyncGenerator, List, Tuple

from aiomqtt import Client as MqttClient
from pyModbusTCP.client import ModbusClient
from tenacity import retry, stop_after_attempt, wait_fixed

from zero_termodinamica.addresses import Address
from zero_termodinamica.settings import ModbusSettings, MqttSettings


class ModbusToMQTTBridge:
    def __init__(
        self,
        modbus: ModbusClient,
        mqtt: MqttClient,
        addresses: List[Address],
        probe_interval: float = 10.0,
    ):
        self._mqtt = mqtt
        self._modbus = modbus
        self.addresses = addresses
        self.probe_interval = probe_interval

    @asynccontextmanager
    @staticmethod
    async def from_settings(
        modbus_settings: ModbusSettings,
        mqtt_settings: MqttSettings,
        addresses: List[Address],
    ) -> "AsyncGenerator[ModbusToMQTTBridge, None]":
        """
        Create a ModbusReader instance from Modbus settings.
        """
        modbus = ModbusClient(
            host=modbus_settings.modbus_host, port=modbus_settings.modbus_port
        )
        async with mqtt_settings.mqtt_client() as mqtt:
            yield ModbusToMQTTBridge(
                modbus, mqtt, addresses, modbus_settings.modbus_probe_interval
            )

    async def run(self) -> None:
        while True:
            async with TaskGroup() as tg:
                tg.create_task(asyncio.sleep(self.probe_interval))
                tg.create_task(self.run_once())

    async def run_once(self) -> None:
        # Read modbus
        modbus_values = self.read_modbus()
        # Scale values
        scaled_values = self.scale_values(modbus_values)
        # Form json
        json_data = self.create_topics(scaled_values)
        # Publish to MQTT
        for topic, data in json_data:
            await self.publish_to_mqtt(topic, data)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def read_modbus(self) -> List[Tuple[Address, int]]:
        try:
            self._modbus.open()
            result = []
            for address in self.addresses:
                value = self._modbus.read_holding_registers(address.register, 1)
                if value and len(value) == 1:
                    result.append((address, value[0]))
                else:
                    logging.warning(
                        f"Received invalid value {value} from register {address.register}"
                    )
            return result
        finally:
            self._modbus.close()

    def scale_values(
        self, modbus_values: List[Tuple[Address, int]]
    ) -> List[Tuple[Address, float]]:
        return [
            (address, self.scale_value(address, value))
            for address, value in modbus_values
        ]

    def scale_value(self, address: Address, value: int) -> float:
        return float(value) * address.scale_factor

    def create_topics(
        self, modbus_values: List[Tuple[Address, float]]
    ) -> List[Tuple[str, str]]:
        result = []
        for topic, values in groupby(modbus_values, key=lambda x: x[0].topic):
            result.append((topic, self._create_json(list(values))))
        return result

    def _create_json(self, modbus_values: List[Tuple[Address, float]]) -> str:
        result = {}
        for address, value in modbus_values:
            result[address.field_name] = value
        return json.dumps(result)

    async def publish_to_mqtt(self, topic: str, data: str) -> None:
        await self._mqtt.publish(topic, data, qos=1)
