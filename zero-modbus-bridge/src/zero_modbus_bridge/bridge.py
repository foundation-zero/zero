"""Core bridge: Modbus TCP → MQTT using ModbusReader + MqttPublisher."""

import asyncio
import logging

from faststream.mqtt import MQTTBroker
from pyModbusTCP.client import ModbusClient

from zero_modbus_bridge.io import ModbusTopic
from zero_modbus_bridge.publisher import MqttPublisher, TopicPublisher
from zero_modbus_bridge.reader import ModbusReader
from zero_modbus_bridge.settings import ModbusSettings

logger = logging.getLogger(__name__)


class ModbusBridge:
    """Lightweight entrypoint composing ``ModbusReader`` and a topic publisher."""

    def __init__(
        self,
        reader: ModbusReader,
        publisher: TopicPublisher,
        topics: list[ModbusTopic],
        probe_interval: float = 10.0,
    ):
        self._reader = reader
        self._publisher = publisher
        self._probe_interval = probe_interval

    @staticmethod
    def from_settings(
        modbus_settings: ModbusSettings,
        broker: MQTTBroker,
        topics: list[ModbusTopic],
    ) -> "ModbusBridge":
        reader = ModbusReader(modbus_settings.modbus_client(), topics)
        publisher = MqttPublisher(broker, topics)
        return ModbusBridge(
            reader,
            publisher,
            topics,
            modbus_settings.modbus_probe_interval,
        )

    @classmethod
    def from_address(
        cls,
        host: str,
        port: int,
        publisher: TopicPublisher,
        topics: list[ModbusTopic],
        probe_interval: float = 10.0,
    ) -> "ModbusBridge":
        """Bridge sharing a publisher while dialing its own gateway address.

        Complements ``from_settings`` for setups with several gateways feeding
        one (parametrized) publisher.
        """
        reader = ModbusReader(ModbusClient(host, port, auto_open=False), topics)
        return cls(reader, publisher, topics, probe_interval)

    async def run(self) -> None:
        loop = asyncio.get_running_loop()
        next_probe_at = loop.time()
        while True:
            await self.run_once()
            next_probe_at += self._probe_interval
            await asyncio.sleep(max(0.0, next_probe_at - loop.time()))

    async def run_once(self) -> None:
        if not self._reader.ensure_open():
            logger.warning("Modbus connection not available - skipping probe")
            return
        for topic_name, payload in self._reader.read_all():
            await self._publisher.publish(topic_name, payload)
