import asyncio
import json
from typing import List

from aiomqtt import Client

from io_processing.config import MQTTConfig
from io_processing.io_list.types import IOTopic
import logging

logger = logging.getLogger(__name__)


class Generator:
    def __init__(
        self, interval: int | float, mqtt_config: MQTTConfig, topics: List[IOTopic]
    ):
        self.interval: int | float = interval
        self.mqtt_config: MQTTConfig = mqtt_config
        self.topics: List[IOTopic] = topics

    async def _send_values(self, client: Client):
        logger.info(
            f"Sending values to {len(self.topics)} topics with an interval of {self.interval}"
        )
        for topic in self.topics:
            next_value = self._next_value(topic)
            await client.publish(topic.topic, json.dumps(next_value))

    async def run(self):
        async with Client(self.mqtt_config.host, port=self.mqtt_config.port) as client:
            while True:
                sleep_task = asyncio.sleep(self.interval)
                send_task = self._send_values(client)

                await asyncio.gather(send_task, sleep_task)

    def _next_value(self, topic: IOTopic):
        return {
            field.name: self._next_field_value(field.data_type)
            for field in topic.fields
        }

    @staticmethod
    def _next_field_value(data_type: str):
        match data_type:
            case "BOOLEAN":
                return False
            case "REAL":
                return 100.5
            case "BIGINT":
                return 10
            case "INTEGER":
                return 1
        raise KeyError(f"Unknown type: {data_type}")
