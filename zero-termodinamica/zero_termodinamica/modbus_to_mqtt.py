import asyncio
import json
import logging
from ast import mod
from asyncio import TaskGroup
from contextlib import asynccontextmanager
from itertools import groupby
from typing import AsyncGenerator, Dict, List, Tuple

from aiomqtt import Client as MqttClient
from pyModbusTCP.client import ModbusClient
from tenacity import retry, stop_after_attempt, wait_fixed

from zero_termodinamica.addresses import Address, ModbusUnit
from zero_termodinamica.settings import ModbusSettings, MqttSettings


class ModbusToMQTTBridge:
    def __init__(
        self,
        modbus: ModbusClient,
        mqtt: MqttClient,
        modbus_units: List[ModbusUnit],
        probe_interval: float = 10.0,
    ):
        self._mqtt = mqtt
        self._modbus = modbus
        self.modbus_units = modbus_units
        self.probe_interval = probe_interval

    @asynccontextmanager
    @staticmethod
    async def from_settings(
        modbus_settings: ModbusSettings,
        mqtt_settings: MqttSettings,
        modbus_units: List[ModbusUnit],
    ) -> "AsyncGenerator[ModbusToMQTTBridge, None]":
        """
        Create a ModbusReader instance from Modbus settings.
        """

        modbus = ModbusClient(
            host=modbus_settings.modbus_host, port=modbus_settings.modbus_port
        )
        async with mqtt_settings.mqtt_client() as mqtt:
            yield ModbusToMQTTBridge(
                modbus, mqtt, modbus_units, modbus_settings.modbus_probe_interval
            )

    async def run(self) -> None:
        while True:
            logging.info("Probing modbus")
            async with TaskGroup() as tg:
                tg.create_task(asyncio.sleep(self.probe_interval))
                tg.create_task(self.run_once())

    async def run_once(self) -> None:
        try:
            success = self._modbus.open()
            if not success:
                logging.warning(
                    f"Failed to open modbus connection to {self._modbus.host}:{self._modbus.port} - {self._modbus.last_error_as_txt}"
                )
                return
            for unit in self.modbus_units:
                self._modbus.unit_id = unit.unit_id
                for topic in unit.topics:
                    # Read modbus
                    modbus_values = self.read_modbus(unit.unit_id, topic.fields)
                    # Scale values
                    scaled_values = self.scale_values(modbus_values)
                    # Form json
                    json_data = self.create_json(scaled_values)
                    # Publish to MQTT
                    await self.publish_to_mqtt(topic.topic, json_data)
        finally:
            self._modbus.close()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def read_modbus(
        self, unit_id: int, addresses: List[Address]
    ) -> List[Tuple[Address, int]]:
        result = []
        for address in addresses:
            value = self._modbus.read_holding_registers(address.register, 1)
            if value and len(value) == 1:
                result.append((address, value[0]))
            else:
                logging.warning(
                    f"Received invalid value {value} from register {address.register}"
                )
        return result

    def scale_values(
        self, modbus_values: List[Tuple[Address, int]]
    ) -> List[Tuple[Address, float]]:
        return [
            (address, self.scale_value(address, value))
            for address, value in modbus_values
        ]

    def scale_value(self, address: Address, value: int) -> float:
        return float(value) * address.scale_factor

    def create_json(self, modbus_values: List[Tuple[Address, float]]) -> str:
        result = {}
        for address, value in modbus_values:
            result[address.field_name] = value
        return json.dumps(result)

    async def publish_to_mqtt(self, topic: str, data: str) -> None:
        await self._mqtt.publish(topic, data, qos=1)
