import asyncio
from contextlib import asynccontextmanager
from datetime import timedelta
from itertools import count
import json
import logging
from typing import AsyncGenerator


from pyModbusTCP.client import ModbusClient
from aiomqtt import Client as MqttClient
from jsonpath_ng import parse
from tenacity import retry, stop_after_attempt, wait_fixed

from zero_hull_temperature.addresses import PROBE_ADDRESSES, ProbeAddress
from zero_hull_temperature.bit_ops import lsw_registers_to_float
from zero_hull_temperature.mqtt import MqttValue, TemperatureReading, Temperatures
from zero_hull_temperature.settings import ModbusSettings, MqttSettings


class TemperatureReader:
    def __init__(self, modbus: ModbusClient):
        self._modbus = modbus

    @asynccontextmanager
    @staticmethod
    async def from_settings(
        modbus_settings: ModbusSettings,
    ) -> "AsyncGenerator[TemperatureReader, None]":
        """
        Create a TemperatureReader instance from Modbus and MQTT settings.
        """
        modbus = ModbusClient(
            host=modbus_settings.modbus_host, port=modbus_settings.modbus_port
        )
        yield TemperatureReader(modbus)

    async def read_temperatures(self):
        """
        Read temperatures from the Modbus client.
        Yields tuples of (probe address, temperature).
        """
        return await self.read_modbus()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def read_modbus(self):
        try:
            self._modbus.open()
            return [item async for item in self._read_modbus_temperatures()]
        finally:
            self._modbus.close()

    async def _read_modbus_temperatures(
        self,
    ) -> AsyncGenerator[TemperatureReading, None]:
        for probe_address in PROBE_ADDRESSES:
            yield TemperatureReading(
                sensor=probe_address.sensor,
                temperature=self._read_modbus_temperature(probe_address),
            )

    def _read_modbus_temperature(self, address: ProbeAddress) -> float:
        """
        Read temperature from a specific probe address.
        Returns the temperature in Celsius.
        """
        result = self._modbus.read_holding_registers(address.register, 2)
        if result:
            return lsw_registers_to_float(result)
        else:
            raise ValueError(f"Failed to read temperature from {address}")


class RelaySwitchingTemperatureReader(TemperatureReader):
    def __init__(
        self,
        modbus: ModbusClient,
        mqtt: MqttClient,
        activate_topic: str,
        activate_json_path: str,
        send_topic: str,
    ):
        super().__init__(modbus)
        self._mqtt = mqtt
        self._activation_topic = activate_topic
        self._activate_json_path = parse(activate_json_path)
        self._send_topic = send_topic

    @asynccontextmanager
    @staticmethod
    async def from_settings(  # type: ignore
        modbus_settings: ModbusSettings,
        mqtt_settings: MqttSettings,
        activate_topic: str,
        activate_json_path: str,
        send_topic: str,
    ) -> "AsyncGenerator[RelaySwitchingTemperatureReader, None]":
        """
        Create a RelaySwitchingTemperatureReader instance from settings.
        """
        async with mqtt_settings.mqtt_client() as mqtt:
            yield RelaySwitchingTemperatureReader(
                modbus_settings.modbus_client(),
                mqtt,
                activate_topic,
                activate_json_path,
                send_topic,
            )

    async def step(self):
        """
        Step function to read temperatures and send them via MQTT.
        """
        logging.info("Reading temperatures")
        temperatures = await self.read_temperatures()
        await self.send_temperatures(temperatures)

    async def run(self, interval: timedelta, n: int = -1):
        for i in count(start=1):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.step())
                tg.create_task(asyncio.sleep(interval.total_seconds()))
            if i == n:
                break

    async def _send_activate(self, activate: bool):
        """
        Send MQTT message to activate or deactivate the Modbus reader.
        """
        payload = self._activate_json_path.update_or_create(
            {}, MqttValue(value=activate).model_dump()
        )
        await self._mqtt.publish(self._activation_topic, json.dumps(payload), qos=1)

    async def read_temperatures(self):
        async with self.activated_hes():
            return await super().read_temperatures()

    async def send_temperatures(self, temperatures: list[TemperatureReading]):
        """
        Send temperature readings to the MQTT broker.
        """
        await self._mqtt.publish(
            self._send_topic,
            Temperatures(temperatures=temperatures).model_dump_json(),
            qos=1,
        )

    @asynccontextmanager
    async def activated_hes(self):
        """
        Context manager to activate the HES reader.
        """

        await self._send_activate(True)
        try:
            yield
        finally:
            await self._send_activate(False)
