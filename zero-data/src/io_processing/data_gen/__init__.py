import asyncio

from io_processing.config import MQTTConfig, io_lists
from io_processing.data_gen.generator import Generator
from io_processing.io_list import read_io_list
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def generate_data():
    logger.info("Generating data for all IO lists")
    mqtt_config = MQTTConfig()  # pyright: ignore

    for source, file_name in io_lists:
        logger.debug(f"Processing {source} {file_name}")
        io_result = read_io_list(Path(f"io_lists/{file_name}"), source)

        generator = Generator(10, mqtt_config, io_result.topics)
        asyncio.run(generator.run())
