import asyncio
import logging
from pathlib import Path

from zero_data.config import MQTTConfig, io_lists
from zero_data.data_gen.generator import Generator
from zero_data.data_gen.marpower_generator import MarpowerGenerator
from zero_data.data_gen.sail_system_generator import SailSystemGenerator
from zero_data.io_list import read_io_list
from zero_data.io_list.types import Source

logger = logging.getLogger(__name__)

_GENERATORS: dict[Source, type[Generator]] = {
    "marpower": MarpowerGenerator,
    "sail_system": SailSystemGenerator,
}


async def _run_all_generators(
    mqtt_config: MQTTConfig,
    excluded_io_list_names: list[str] | None = None,
    cache_dir: Path | None = None,
):
    """Run all data generators concurrently."""
    excluded_set: set[str] = set(excluded_io_list_names or [])

    async with asyncio.TaskGroup() as tg:
        for source, file_names in io_lists:
            if source in excluded_set:
                logger.info(f"Skipping {source}; excluded by name")
                continue

            paths = [Path(f"io_lists/{file_name}") for file_name in file_names]
            logger.debug(f"Processing {source} {paths}")
            topics = read_io_list(paths, source, cache_dir=cache_dir).topics
            logger.info(f"Starting {source} generator for {len(topics)} topics")
            tg.create_task(_GENERATORS[source](10, mqtt_config, topics).run())


def generate_data(
    excluded_io_list_names: list[str] | None = None, cache_dir: Path | None = None
):
    """Generate data for all IO lists."""
    logger.info("Generating data for all IO lists")
    if excluded_io_list_names:
        logger.info(f"Excluding IO lists: {excluded_io_list_names}")
    mqtt_config = MQTTConfig()  # pyright: ignore
    logger.info(f"Using MQTTConfig: {mqtt_config.model_dump_json()}")
    asyncio.run(_run_all_generators(mqtt_config, excluded_io_list_names, cache_dir))
