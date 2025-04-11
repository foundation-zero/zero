import asyncio
import json
from typing import List

from aiomqtt import Client

from io_processing.config import MQTTConfig
from io_processing.io_list.types import IOTopic
import logging

import random


logger = logging.getLogger(__name__)


class Generator:
    def __init__(
        self,
        interval: int | float,
        mqtt_config: MQTTConfig,
        topics: List[IOTopic],
        source: str,
    ):
        self.interval: int | float = interval
        self.mqtt_config: MQTTConfig = mqtt_config
        self.topics: List[IOTopic] = topics

    async def _send_values(self, client: Client):
        """Send values to the MQTT broker at regular intervals."""
        logger.info(
            f"Sending values to {len(self.topics)} topics with an interval of {self.interval}"
        )
        for topic in self.topics:
            next_value = self._next_value(topic)
            await client.publish(topic.topic, json.dumps(next_value))

    async def run(self):
        """Run the generator, sending values at regular intervals."""
        async with Client(self.mqtt_config.host, port=self.mqtt_config.port) as client:
            while True:
                sleep_task = asyncio.sleep(self.interval)
                send_task = self._send_values(client)

                await asyncio.gather(send_task, sleep_task)

    def _next_value(self, topic: IOTopic):
        """Generate the next value for a given topic."""
        return {
            field.name: self._next_field_value(field.data_type)
            for field in topic.fields
        }

    @staticmethod
    def _next_field_value(data_type: str):
        """Generate a random value based on the data type."""
        match data_type:
            case "BOOLEAN":
                return random.choice([True, False])
            case "REAL":
                return random.normalvariate(mu=10, sigma=1.0)
            case "BIGINT":
                return random.randint(0, 100)
            case "INTEGER":
                return random.binomialvariate(n=10, p=0.5)
        raise KeyError(f"Unknown type: {data_type}")
