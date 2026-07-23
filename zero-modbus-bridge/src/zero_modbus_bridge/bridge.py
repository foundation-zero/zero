"""Core bridge: Modbus TCP → MQTT using ModbusReader + MqttPublisher."""

import asyncio
import logging

from faststream.mqtt import MQTTBroker
from pyModbusTCP.client import ModbusClient

from zero_modbus_bridge.io import ModbusTopic
from zero_modbus_bridge.publisher import MqttPublisher
from zero_modbus_bridge.reader import ModbusReader
from zero_modbus_bridge.settings import ModbusSettings

logger = logging.getLogger(__name__)


class ModbusBridge:
    """Lightweight entrypoint composing ``ModbusReader`` and ``MqttPublisher``."""

    def __init__(
        self,
        modbus: ModbusClient,
        broker: MQTTBroker,
        topics: list[ModbusTopic],
        probe_interval: float = 10.0,
    ):
        self._broker = broker
        self._modbus = modbus
        self._reader = ModbusReader(modbus, topics)
        self._publisher = MqttPublisher(broker, topics)
        self._probe_interval = probe_interval

    @staticmethod
    def from_settings(
        modbus_settings: ModbusSettings,
        broker: MQTTBroker,
        topics: list[ModbusTopic],
    ) -> "ModbusBridge":
        return ModbusBridge(
            modbus_settings.modbus_client(),
            broker,
            topics,
            modbus_settings.modbus_probe_interval,
        )

    async def run(self) -> None:
        loop = asyncio.get_running_loop()
        next_probe_at = loop.time()
        while True:
            await self.run_once()
            next_probe_at += self._probe_interval
            await asyncio.sleep(max(0.0, next_probe_at - loop.time()))

    async def run_once(self) -> None:
        if not self._modbus.is_open:
            if not self._modbus.open():
                logger.warning(
                    f"Failed to open modbus connection to "
                    f"{self._modbus.host}:{self._modbus.port} - "
                    f"{self._modbus.last_error_as_txt}"
                )
                return
        async for topic_name, payload in self._reader.read_all():
            await self._publisher.publish(topic_name, payload)
