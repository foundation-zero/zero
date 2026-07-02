import asyncio
import json
import logging
from asyncio import TaskGroup
from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Tuple

from aiomqtt import Client as MqttClient
from pymodbus.client import AsyncModbusSerialClient
from pymodbus.exceptions import ModbusException
from tenacity import retry, stop_after_attempt, wait_fixed

from zero_termodinamica.io import Address, LiteralField, ModbusUnit
from zero_termodinamica.settings import (
    ModbusSerialSettings,
    MqttSettings,
)


class ModbusRtuToMqttBridge:
    def __init__(
        self,
        modbus: AsyncModbusSerialClient,
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
        modbus_settings: ModbusSerialSettings,
        mqtt_settings: MqttSettings,
        modbus_units: List[ModbusUnit],
    ) -> "AsyncGenerator[ModbusRtuToMqttBridge, None]":
        """
        Create a ModbusReader instance from Modbus settings.
        """

        modbus = AsyncModbusSerialClient(
            port=modbus_settings.modbus_serial_port,
            baudrate=modbus_settings.baudrate,
            bytesize=modbus_settings.bytesize,
            parity=modbus_settings.parity,
            stopbits=modbus_settings.stopbits,
        )
        async with mqtt_settings.mqtt_client() as mqtt:
            yield ModbusRtuToMqttBridge(
                modbus, mqtt, modbus_units, modbus_settings.modbus_probe_interval
            )

    async def run(self) -> None:
        while True:
            logging.info("Probing modbus")
            async with TaskGroup() as tg:
                tg.create_task(asyncio.sleep(self._probe_interval))
                tg.create_task(self.run_once())

    async def run_once(self) -> None:
        await self._modbus.connect()
        if not self._modbus.connected:
            logging.warning("Modbus not connected")
            self._modbus.close()
        for unit in self._modbus_units:
            for topic in unit.topics:
                modbus_values = await self.read_modbus(
                    topic.modbus_fields, unit.unit_id
                )
                scaled_values = self.scale_values(modbus_values)
                json_data = self.create_json(scaled_values, topic.extra_fields)
                await self.publish_to_mqtt(topic.topic, json_data)
        self._modbus.close()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def read_modbus(
        self, addresses: List[Address], device_id: int
    ) -> List[Tuple[Address, int]]:
        result = []
        for address in addresses:
            try:
                # Hardcoded at 1 register. In the future this could be done from the Address class (parsed from IO list) (or in blocks smartly derived from the addresses)
                rr = await self._modbus.read_holding_registers(
                    address.modbus_register, count=1, device_id=device_id
                )
                value = rr.registers[0]
                result.append((address, value))
            except ModbusException as exc:
                logging.error(f"ERROR: exception in pymodbus {exc}")
                self._modbus.close()
                raise exc
            if rr.isError():
                logging.error("ERROR: pymodbus returned an error!")
                self._modbus.close()
                raise ModbusException(value)

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
