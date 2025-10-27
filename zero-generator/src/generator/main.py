import asyncio
import logging
import random
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from aiomqtt import Client as MqttClient

from .config import Settings

logger = logging.getLogger("generator")


class DataGenerator:
    def __init__(self, mqtt_client: MqttClient):
        self._mqtt_client: MqttClient = mqtt_client
        self.running: bool = False
        self.config: list[dict] = []
        self.tasks: list[asyncio.Task] = []

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        async with MqttClient(
            settings.mqtt_host, settings.mqtt_port, identifier="generator"
        ) as mqtt_client:
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
                    "values": (
                        ("justanint", "int"),
                        ("aws", ["float", 0, 180]),
                        ("pcs_mode", ["enum", ["propulsion", "idle", "regeneration"]]),
                    ),
                },
            ]
        """
        if self.running:
            raise Exception("Data generator is already running.")
        else:
            logger.info("Starting data generator...")
            self.config = config
            for topic_config in config:
                topic = topic_config.get("topic")
                interval = topic_config.get("interval")
                values = topic_config.get("values")

                if not topic or not interval or not values:
                    raise ValueError(
                        f"topic, interval, and values must be defined: {topic}, {interval}, {values}"
                    )
                else:
                    logger.debug(f"Creating task for topic: {topic}")
                    self.tasks.append(
                        asyncio.create_task(
                            self._generate_single_topic(topic, interval, values)
                        )
                    )

            self.running = True

            await asyncio.gather(*self.tasks, return_exceptions=True)

    async def stop(self):
        """Stops the data generation by cancelling all running tasks."""
        for t in self.tasks:
            t.cancel()
        self.tasks = []
        self.running = False

    async def _generate_single_topic(
        self, topic: str, interval: float, values: list[tuple]
    ):
        while True:
            logger.info(f"sending message on topic: {topic} with interval {interval}")
            send_task = self._mqtt_client.publish(topic, self._determine_values(values))
            sleep_task = asyncio.sleep(interval)
            await asyncio.gather(send_task, sleep_task)

    def _determine_values(self, values: list[tuple]) -> str:
        determined_values = {}
        for field, value in values:
            if isinstance(value, str):
                determined_values[field] = self._default_value(value)
            elif isinstance(value, list):
                if value[0] == "enum":
                    data_type, choices = value
                    determined_values[field] = random.choice(choices)
                else:
                    data_type, lower_bound, upper_bound = value
                    determined_values[field] = self._default_value(
                        data_type, int(lower_bound), int(upper_bound)
                    )
            elif callable(value):
                determined_values[field] = value()
            else:
                raise ValueError(f"Unsupported value type: {value}")

        return str(determined_values)

    def _default_value(
        self, data_type: str, lower_bound: int = 0, upper_bound: int = 100
    ):
        match data_type:
            case "int":
                return random.randint(lower_bound, upper_bound)
            case "float":
                return random.uniform(lower_bound, upper_bound)
            case "boolean":
                return random.choice([True, False])
            case "string":
                return "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))
            case "timestamp":
                return datetime.now(tz=UTC)
            case _:
                raise ValueError(f"Unsupported data type: {data_type}")
