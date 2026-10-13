"""Relay-switching Modbus-to-MQTT bridge for hull temperature."""

import json
import logging

from faststream.mqtt import MQTTBroker, QoS
from jsonpath_ng import parse
from zero_modbus_bridge.bridge import TRANSIENT_PUBLISH_ERRORS, ModbusBridge
from zero_modbus_bridge.io import ModbusTopic
from zero_modbus_bridge.publisher import TopicPublisher
from zero_modbus_bridge.reader import ModbusReader
from zero_modbus_bridge.settings import ModbusSettings

from zero_hull_temperature.addresses import (
    HULL_TEMPERATURE_TOPIC,
    PATH,
    TOPIC,
    create_publisher,
)
from zero_hull_temperature.mqtt import MqttValue

logger = logging.getLogger(__name__)

BUFFER_SECONDS = 300


def buffer_size_for(probe_interval: float, topic_count: int) -> int:
    """Readings produced in ``BUFFER_SECONDS`` of probing, at least one probe's worth."""
    return max(1, round(BUFFER_SECONDS / probe_interval)) * topic_count


class RelaySwitchingBridge(ModbusBridge):
    """Modbus-to-MQTT bridge that activates a relay before each Modbus read."""

    def __init__(
        self,
        reader: ModbusReader,
        publisher: TopicPublisher,
        broker: MQTTBroker,
        topics: list[ModbusTopic],
        probe_interval: float = 10.0,
        *,
        activate_topic: str = TOPIC,
        activate_json_path: str = PATH,
        buffer_size: int,
    ):
        super().__init__(
            reader, publisher, topics, probe_interval, buffer_size=buffer_size
        )
        self._relay_broker = broker
        self._activate_topic = activate_topic
        self._activate_json_path = parse(activate_json_path)

    @staticmethod
    def from_settings(  # type: ignore[override]
        modbus_settings: ModbusSettings,
        broker: MQTTBroker,
        activate_topic: str = TOPIC,
        activate_json_path: str = PATH,
    ) -> "RelaySwitchingBridge":
        topics: list[ModbusTopic] = [HULL_TEMPERATURE_TOPIC]
        return RelaySwitchingBridge(
            ModbusReader(modbus_settings.modbus_client(), topics),
            create_publisher(broker),
            broker,
            topics,
            modbus_settings.modbus_probe_interval,
            activate_topic=activate_topic,
            activate_json_path=activate_json_path,
            buffer_size=buffer_size_for(
                modbus_settings.modbus_probe_interval, len(topics)
            ),
        )

    async def run_once(self) -> None:
        await self._send_activate(True)
        await super().run_once()

    async def _send_activate(self, activate: bool) -> None:
        payload = self._activate_json_path.update_or_create(
            {}, MqttValue.model_construct(value=activate).model_dump(by_alias=True)
        )
        try:
            await self._relay_broker.publish(
                json.dumps(payload), self._activate_topic, qos=QoS.AT_LEAST_ONCE
            )
        except TRANSIENT_PUBLISH_ERRORS as exc:
            logger.warning(
                "Relay activation not published (broker unavailable?): %r", exc
            )
