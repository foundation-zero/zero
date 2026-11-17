import asyncio
import logging
from contextlib import asynccontextmanager

from aiomqtt import Client as MqttClient

from .base import GeneratorConfig
from .config import Settings

logger = logging.getLogger("generator")


class DataGenerator:
    def __init__(self, mqtt_client: MqttClient):
        self._mqtt_client: MqttClient = mqtt_client
        self.config: list[GeneratorConfig] = []

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings, identifier: str = "generator"):
        async with MqttClient(
            settings.mqtt_host, settings.mqtt_port, identifier=identifier
        ) as mqtt_client:
            yield DataGenerator(mqtt_client=mqtt_client)

    async def generate(self, config: list[GeneratorConfig]):
        """
        Asynchronously generates data for multiple topics based on the provided configuration.

        Args:
            config (list[GeneratorConfig]): List of GeneratorConfig objects, each containing:
            - topic (str): The topic name.
            - interval (int): Interval in seconds between data generations.
            - values (dict[str, Generator]): Value definitions for the topic.

        Example:
            import generator as gen

            config = [
                GeneratorConfig(
                    topic="topic/test",
                    interval=10,
                    values={
                        "justanint": gen.int_(),
                        "aws": gen.float_(0, 180),
                        "pcs_mode": gen.choice(["propulsion", "idle", "regeneration"]),
                    }
                )
            ]
        """
        logger.info("Starting data generator...")
        try:
            async with asyncio.TaskGroup() as group:
                for topic_config in config:
                    logger.debug(f"Creating task for topic: {topic_config.topic}")
                    group.create_task(self._generate_single_topic(topic_config))

        except Exception:
            logger.info("Data generator stopped due to an exception.")
            raise

    async def _generate_single_topic(self, config: GeneratorConfig):
        while True:
            logger.info(
                f"sending message on topic: {config.topic} with interval {config.interval}"
            )
            send_task = self._mqtt_client.publish(config.topic, config.generator.gen())
            sleep_task = asyncio.sleep(config.interval)
            await asyncio.gather(send_task, sleep_task)
