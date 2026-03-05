import asyncio
from pathlib import Path

from zero_data.config import MQTTConfig, io_lists
from zero_data.data_gen.generator import Generator
from zero_data.data_gen.marpower_generator import MarpowerGenerator
from zero_data.data_gen.sail_system_generator import SailSystemGenerator
from zero_data.io_list import read_io_list
from zero_data.io_list.types import Source
import logging

logger = logging.getLogger(__name__)

_GENERATORS: dict[Source, type[Generator]] = {
    "marpower": MarpowerGenerator,
    "sail_system": SailSystemGenerator,
}


async def _run_all_generators(mqtt_config: MQTTConfig):
    """Run all data generators concurrently."""
    async with asyncio.TaskGroup() as tg:
        for source, file_names in io_lists:
            paths = [Path(f"io_lists/{file_name}") for file_name in file_names]
            logger.debug(f"Processing {source} {paths}")
            topics = read_io_list(paths, source).topics
            logger.info(f"Starting {source} generator for {len(topics)} topics")
            tg.create_task(_GENERATORS[source](10, mqtt_config, topics).run())


def generate_data():
    """Generate data for all IO lists."""
    logger.info("Generating data for all IO lists")
    mqtt_config = MQTTConfig()  # pyright: ignore
    logger.info(f"Using MQTTConfig: {mqtt_config.model_dump_json()}")
    asyncio.run(_run_all_generators(mqtt_config))
