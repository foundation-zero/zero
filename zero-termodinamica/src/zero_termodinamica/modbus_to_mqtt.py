import asyncio
import json
import logging
from asyncio import TaskGroup
from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Tuple

from aiomqtt import Client as MqttClient
from pyModbusTCP.client import ModbusClient
from tenacity import retry, stop_after_attempt, wait_fixed

from zero_termodinamica.io import Address, LiteralField, ModbusUnit
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
        self._modbus_units = modbus_units
        self._probe_interval = probe_interval

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
                tg.create_task(asyncio.sleep(self._probe_interval))
                tg.create_task(self.run_once())

    async def run_once(self) -> None:
        try:
            success = self._modbus.open()
            if not success:
                logging.warning(
                    f"Failed to open modbus connection to {self._modbus.host}:{self._modbus.port} - {self._modbus.last_error_as_txt}"
                )
                return
            for unit in self._modbus_units:
                self._modbus.unit_id = unit.unit_id
                for topic in unit.topics:
                    modbus_values = self.read_modbus(topic.modbus_fields)
                    scaled_values = self.scale_values(modbus_values)
                    json_data = self.create_json(scaled_values, topic.extra_fields)
                    await self.publish_to_mqtt(topic.topic, json_data)
        finally:
            self._modbus.close()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def read_modbus(self, addresses: List[Address]) -> List[Tuple[Address, int]]:
        result = []
        has_fault = False
        for address in addresses:
            # Hardcoded at 1 register. In the future this could be done from the Address class (parsed from IO list) (or in blocks smartly derived from the addresses)
            value = self._modbus.read_holding_registers(address.modbus_register, 1)
            if value and len(value) == 1:
                result.append((address, value[0]))
            else:
                logging.warning(
                    f"Received invalid value {value} from register {address.modbus_register}"
                )
                has_fault = True
        if has_fault:
            # Try all registers (instead of failing) to get logging, but dont process None values
            result = []

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

    def create_json(
        self,
        modbus_values: List[Tuple[Address, float]],
        extra_fields: List[LiteralField],
    ) -> str:
        extra_fields_dict = {f.field_name: f.value for f in extra_fields}
        modbus_fields = {address.field_name: value for address, value in modbus_values}
        result = {**extra_fields_dict, **modbus_fields}

        return json.dumps(result)

    async def publish_to_mqtt(self, topic: str, data: str) -> None:
        await self._mqtt.publish(topic, data, qos=1)
