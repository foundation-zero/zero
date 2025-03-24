import asyncio

from io_processing.config import MQTTConfig, io_lists
from io_processing.data_gen.generator import Generator
from io_processing.io_list import read_io_list
from pathlib import Path


def generate_data():
    mqtt_config = MQTTConfig()  # pyright: ignore

    for source, file_name in io_lists:
        io_result = read_io_list(Path(f"io_lists/{file_name}"), source)

        generator = Generator(10, mqtt_config, io_result.topics)
        asyncio.run(generator.run())
