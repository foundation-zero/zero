import asyncio
from typing import Annotated, Any, List

from aiomqtt import Client

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from pydantic.alias_generators import to_pascal
from zero_data.config import MQTTConfig
from zero_data.io_list.types import IOTopic
import logging

import random

from datetime import UTC, datetime

logger = logging.getLogger(__name__)

class MarpowerMessage[T](BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_pascal
    )
    value: T
    timestamp: Annotated[datetime, Field(alias="TimeStamp")]
    is_valid: bool = True
    has_value: bool = True


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

    async def _send_messages(self, client: Client):
        """Send values to the MQTT broker at regular intervals."""
        logger.info(
            f"Sending values to {len(self.topics)} topics with an interval of {self.interval}"
        )
        for topic in self.topics:
            next_value = self._message(topic)
            # Using pydantic to ensure dates are ISO format
            payload = TypeAdapter(dict[str, dict[str, Any]]).dump_json(next_value, by_alias=True)
            await client.publish(topic.topic, payload)

    async def run(self):
        """Run the generator, sending messages at regular intervals."""
        async with Client(self.mqtt_config.host, port=self.mqtt_config.port) as client:
            while True:
                sleep_task = asyncio.sleep(self.interval)
                send_task = self._send_messages(client)

                await asyncio.gather(send_task, sleep_task)

    def _message(self, topic: IOTopic):
        """Generate the next message for a given topic."""
        content = {
            field.name: self._random_message(field.data_type).model_dump(by_alias=True)
            for field in topic.fields
        }
        return content

    @staticmethod
    def _random_message(data_type: str) -> MarpowerMessage:
        """Generate a random value based on the data type."""
        match data_type:
            case "BOOLEAN":
                return Generator._generate_marpower_message(
                    random.choice([True, False]),
                )
            case "REAL":
                return Generator._generate_marpower_message(
                    random.normalvariate(mu=10, sigma=1.0)
                )
            case "BIGINT":
                return Generator._generate_marpower_message(
                    random.randint(0, 100)
                )
            case "INTEGER":
                return Generator._generate_marpower_message(
                    random.binomialvariate(n=10, p=0.5)
                )
            case "TIMESTAMP":
                return Generator._generate_marpower_message(
                    datetime.now(tz=UTC)
                )
            case "STRING":
                return Generator._generate_marpower_message(
                    "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))
                )
        raise KeyError(f"Unknown type: {data_type}")
    
    @staticmethod
    def _generate_marpower_message[T](value: T) -> MarpowerMessage[T]:
        return MarpowerMessage[T](
            value=value,
            timestamp=datetime.now(tz=UTC),
            is_valid=True,
            has_value=True
        )
