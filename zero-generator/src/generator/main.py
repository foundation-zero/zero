import asyncio
import logging
from contextlib import asynccontextmanager

from aiomqtt import Client as MqttClient

from .base import Generator
from .config import Settings

logger = logging.getLogger("generator")


class DataGenerator:
    def __init__(self, mqtt_client: MqttClient):
        self._mqtt_client: MqttClient = mqtt_client
        self.config: list[dict] = []

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        async with MqttClient(settings.mqtt_host, settings.mqtt_port, identifier="generator") as mqtt_client:
            yield DataGenerator(mqtt_client=mqtt_client)

    async def generate(self, config: list[dict]):
        """
        Asynchronously generates data for multiple topics based on the provided configuration.
        Args:
            config (list): A list of dictionaries, each containing:
                - topic (str): The name of the topic.
                - interval (int): The interval in seconds between data generations.
                - values (tuple): A tuple of value definitions for the topic.

        Example:
            config = [
                {
                    "topic": "topic/test",
                    "interval": 10,
                    "values": {
                        "justanint": RandomGenerator("int"),
                        "aws": RandomGenerator("float", 0, 180),
                        "pcs_mode": RandomChoiceGenerator("enum", ["propulsion", "idle", "regeneration"]),
                    },
                },
            ]
        """
        logger.info("Starting data generator...")
        self.config = config
        try:
            async with asyncio.TaskGroup() as group:
                for topic_config in config:
                    topic = topic_config.get("topic")
                    interval = topic_config.get("interval")
                    values = topic_config.get("values")

                    if not topic or not interval or not values:
                        raise ValueError(f"topic, interval, and values must be defined: {topic}, {interval}, {values}")
                    else:
                        logger.debug(f"Creating task for topic: {topic}")
                        group.create_task(self._generate_single_topic(topic, interval, values))

        except Exception:
            logger.info("Data generator stopped due to an exception.")
            raise

    async def _generate_single_topic(self, topic: str, interval: float, values: dict[str, Generator]):
        while True:
            logger.info(f"sending message on topic: {topic} with interval {interval}")
            send_task = self._mqtt_client.publish(topic, self._determine_values(values))
            sleep_task = asyncio.sleep(interval)
            await asyncio.gather(send_task, sleep_task)

    def _determine_values(self, values: dict[str, Generator]) -> str:
        return str({field: generator.gen() for field, generator in values.items()})
