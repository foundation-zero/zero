import asyncio

from zero_data.config import MQTTConfig, io_lists
from zero_data.data_gen.generator import Generator
from zero_data.data_gen.sail_system_generator import SailSystemGenerator
from zero_data.io_list import read_io_list
from zero_data.io_list.readers.sail_system import read_sail_system
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


async def _run_all_generators(mqtt_config: MQTTConfig):
    """Run all data generators concurrently."""
    tasks = []

    for source, file_names in io_lists:
        file_paths = [Path(f"io_lists/{file_name}") for file_name in file_names]
        logger.debug(f"Processing {source} {file_paths}")
        io_result = read_io_list(file_paths, source)
        logger.info(
            f"Starting generator for IO list {file_paths} with Topics:\n{[t.topic for t in io_result.topics]}"
        )
        tasks.append(Generator(10, mqtt_config, io_result.topics).run())

    sail_system_result = read_sail_system()
    logger.info(
        f"Starting sail system generator for {len(sail_system_result.topics)} topics"
    )
    tasks.append(SailSystemGenerator(10, mqtt_config, sail_system_result.topics).run())

    await asyncio.gather(*tasks)


def generate_data():
    """Generate data for all IO lists."""
    logger.info("Generating data for all IO lists")
    mqtt_config = MQTTConfig()  # pyright: ignore
    logger.info(f"Using MQTTConfig: {mqtt_config.model_dump_json()}")
    asyncio.run(_run_all_generators(mqtt_config))
