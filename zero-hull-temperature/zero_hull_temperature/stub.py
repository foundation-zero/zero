import asyncio
from contextlib import asynccontextmanager
import json
from typing import Coroutine
from pyModbusTCP.server import ModbusServer
from aiomqtt import Client as MqttClient
from jsonpath_ng import parse

from zero_hull_temperature.addresses import PROBE_ADDRESSES
from zero_hull_temperature.bit_ops import float_to_lsw_registers
from zero_hull_temperature.mqtt import MqttValue
from zero_hull_temperature.settings import ModbusSettings, MqttSettings

TIME_TO_WAKE = 1  # seconds to wait before enabling Modbus server
TIME_TO_SLEEP = 0


class Stub:
    def __init__(
        self,
        mqtt: MqttClient,
        modbus: ModbusServer,
        topic: str,
        json_path: str,
        default_temperature: float = 20.0,
    ):
        self._mqtt = mqtt
        self._modbus = modbus
        for address in PROBE_ADDRESSES:
            self._modbus.data_bank.set_holding_registers(
                address.register, float_to_lsw_registers(default_temperature)
            )
        self._topic = topic
        self._json_path = parse(json_path)

    @asynccontextmanager
    @staticmethod
    async def from_settings(
        modbus_settings: ModbusSettings,
        mqtt_settings: MqttSettings,
        topic: str,
        json_path: str,
        default_temperature: float,
    ):
        async with mqtt_settings.mqtt_client() as mqtt:
            yield Stub(
                mqtt,
                modbus_settings.modbus_server(),
                topic,
                json_path,
                default_temperature,
            )

    async def _check_for_enable(self):
        async for message in self._mqtt.messages:
            if message.topic.matches(self._topic) and isinstance(
                message.payload, str | bytes
            ):
                payload = (
                    str(message.payload, "utf-8")
                    if isinstance(message.payload, bytes)
                    else message.payload
                )
                data = json.loads(payload)
                result = next(iter(self._json_path.find(data)), None)
                if result:
                    value = MqttValue.model_validate(result.value).value
                    if value:
                        await asyncio.sleep(TIME_TO_WAKE)
                        await self.enable_modbus()
                    else:
                        await asyncio.sleep(TIME_TO_SLEEP)
                        await self.disable_modbus()

    async def enable_modbus(self):
        self._modbus.start()

    async def disable_modbus(self):
        self._modbus.stop()

    async def run(self) -> Coroutine[None, None, None]:
        await self._mqtt.subscribe(self._topic)

        return self._check_for_enable()
