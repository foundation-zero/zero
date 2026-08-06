"""MQTT publisher: registers FastStream publishers and dispatches payloads."""

import logging

from faststream.mqtt import MQTTBroker, QoS
from faststream.mqtt.publisher.usecase import MQTTPublisher
from pydantic import BaseModel

from zero_modbus_bridge.io import ModbusTopic

logger = logging.getLogger(__name__)


class MqttPublisher:
    """Wraps FastStream topic publishers for a set of ModbusTopics.

    Call ``register_publishers`` once per broker to create all publishers,
    then ``publish(topic, payload)`` to send a JSON payload.
    """

    def __init__(self, broker: MQTTBroker, topics: list[ModbusTopic]):
        self._publishers = self.register_publishers(broker, topics)

    @staticmethod
    def register_publishers(
        broker: MQTTBroker,
        topics: list[ModbusTopic],
    ) -> dict[str, MQTTPublisher]:
        """Register one FastStream publisher per topic, return ``topic→publisher`` dict."""
        publishers: dict[str, MQTTPublisher] = {}
        for topic in topics:
            publisher = broker.publisher(
                topic.topic,
                schema=topic.model,
                qos=QoS.AT_LEAST_ONCE,
                description=f"Modbus data for {topic.topic}",
            )
            publishers[topic.topic] = publisher
        return publishers

    async def publish(self, topic: str, payload: BaseModel) -> None:
        """Publish a JSON payload to a previously-registered topic."""
        if publisher := self._publishers.get(topic):
            await publisher.publish(payload)
        else:
            logger.warning("No publisher for topic %s", topic)
