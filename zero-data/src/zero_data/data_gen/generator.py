import asyncio
import json
from abc import abstractmethod
from typing import List

from aiomqtt import Client

from zero_data.config import MQTTConfig
from zero_data.io_list.types import IOTopic, IOValue
import logging

logger = logging.getLogger(__name__)


class Generator:
    def __init__(
        self,
        interval: int | float,
        mqtt_config: MQTTConfig,
        topics: List[IOTopic],
    ):
        self.interval: int | float = interval
        self.mqtt_config: MQTTConfig = mqtt_config
        self.topics: List[IOTopic] = topics

    async def run(self):
        """Run the generator, sending messages at regular intervals."""
        async with Client(self.mqtt_config.host, port=self.mqtt_config.port) as client:
            while True:
                sleep_task = asyncio.sleep(self.interval)
                send_task = self.send_messages(client)

                await asyncio.gather(send_task, sleep_task)

    def get_topic(self, topic: IOTopic):
        return topic.topic

    def serialize_message(self, message):
        return json.dumps(message)

    async def send_messages(self, client: Client):
        """Send values to the MQTT broker at regular intervals."""
        logger.info(
            f"Sending values to {len(self.topics)} topics with an interval of {self.interval}"
        )
        for topic in self.topics:
            next_value = self.generate_message(topic)
            payload = self.serialize_message(next_value)
            await client.publish(self.get_topic(topic), payload)

    def generate_message(self, topic: IOTopic):
        """Generate the next message for a given topic."""
        content = {
            field.name: self.generate_random_value(field) for field in topic.fields
        }
        return content

    @abstractmethod
    def generate_random_value(self, field: IOValue): ...
