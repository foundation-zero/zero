import logging
import sys

from aiomqtt import Client as MqttClient
from generator import DataGenerator

from loads.config import settings

from .definitions import SailSystems

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-8s | %(levelname)-6s | %(message)s",
    stream=sys.stdout,
    force=True,
)


async def main():
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        data_gen = DataGenerator(mqtt_client=client)

        config = SailSystems.gen_config()
        print(config)
        await data_gen.generate(config=config)


def run():
    import asyncio

    asyncio.run(main())
