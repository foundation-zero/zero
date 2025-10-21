import logging

from aiomqtt import Client as MqttClient

from .main import DataGenerator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def run_test():
    async with MqttClient("localhost", 1883, identifier="generator") as mqtt_client:
        gen = DataGenerator(mqtt_client=mqtt_client)

        config = [
            {
                "topic": "test",
                "interval": 1,
                "values": (
                    ("justanint", "int"),
                    ("awa", ["int", 0, 90]),
                    ("aws", ["float", 0, 30]),
                    ("pcs_mode", ("enum", ["propulsion", "idle", "docked"])),
                ),
            },
            {
                "topic": "test2",
                "interval": 2,
                "values": (
                    ("justanint", "int"),
                    ("awa", ["int", 0, 90]),
                    ("aws", ["float", 0, 30]),
                    ("pcs_mode", ("enum", ["propulsion", "idle", "docked"])),
                ),
            },
        ]

        await gen.generate(config)


def main():
    import asyncio

    asyncio.run(run_test())
