import asyncio
import json
from abc import abstractmethod
from typing import Annotated, Any, List

from aiomqtt import Client

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from pydantic.alias_generators import to_pascal
from zero_data.config import MQTTConfig
from zero_data.io_list.types import IOTopic, IOValue
import logging

import random

from datetime import UTC, datetime

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


class MarpowerMessage[T](BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_pascal)
    value: T
    timestamp: Annotated[datetime, Field(alias="TimeStamp")]
    is_valid: bool = True
    has_value: bool = True


class MarpowerGenerator(Generator):
    def get_topic(self, topic: IOTopic):
        return topic.topic.removeprefix("marpower/")

    def serialize_message(self, message):
        return TypeAdapter(dict[str, dict[str, Any]]).dump_json(message, by_alias=True)

    def generate_random_value(self, field: IOValue):
        return self._random_message(field.data_type).model_dump(by_alias=True)

    def _random_message(self, data_type: str) -> MarpowerMessage:
        """Generate a random value based on the data type."""
        match data_type:
            case "BOOLEAN":
                return self._generate_marpower_message(
                    random.choice([True, False]),
                )
            case "REAL":
                return self._generate_marpower_message(
                    random.normalvariate(mu=10, sigma=1.0)
                )
            case "BIGINT":
                return self._generate_marpower_message(random.randint(0, 100))
            case "INTEGER":
                return self._generate_marpower_message(
                    random.binomialvariate(n=10, p=0.5)
                )
            case "TIMESTAMP":
                return self._generate_marpower_message(datetime.now(tz=UTC))
            case "STRING":
                return self._generate_marpower_message(
                    "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))
                )
        raise KeyError(f"Unknown type: {data_type}")

    def _generate_marpower_message[T](self, value: T) -> MarpowerMessage[T]:
        return MarpowerMessage[T](
            value=value, timestamp=datetime.now(tz=UTC), is_valid=True, has_value=True
        )
