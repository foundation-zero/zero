import asyncio
import logging
import os
from collections.abc import Callable
from pathlib import Path

from zero_data.config import MQTTConfig, io_lists
from zero_data.data_gen.atpx_generator import AtpxGenerator
from zero_data.data_gen.atpx_nmea_generator import AtpxNmeaGenerator
from zero_data.data_gen.generator import BaseGenerator, Generator
from zero_data.data_gen.marpower_generator import MarpowerGenerator
from zero_data.data_gen.sail_system_generator import SailSystemGenerator
from zero_data.io_list import read_io_list
from zero_data.io_list.types import IOResult, Source

logger = logging.getLogger(__name__)

__all__ = [
    "AtpxGenerator",
    "AtpxNmeaGenerator",
    "Generator",
    "MarpowerGenerator",
    "SailSystemGenerator",
    "generate_data",
]

_PUBLISH_INTERVAL_SECONDS = 10

# Builds a runnable generator from a source's io_list. Each source maps to one
# builder so generator selection lives in a single dispatch, not a special case.
GeneratorBuilder = Callable[[float, MQTTConfig, IOResult], BaseGenerator]


def _topic_generator(generator_class: type[Generator]) -> GeneratorBuilder:
    def build(
        interval: float, mqtt_config: MQTTConfig, io_result: IOResult
    ) -> BaseGenerator:
        return generator_class(interval, mqtt_config, io_result.topics)

    return build


def _atpx_generator(
    interval: float, mqtt_config: MQTTConfig, io_result: IOResult
) -> AtpxGenerator:
    field_ids = io_result.io_list.sort("id")["id"].to_list()
    prefix = os.environ.get("ATPX_RAW_TOPIC_PREFIX", "atpx")
    return AtpxGenerator(interval, mqtt_config, field_ids, prefix)


_GENERATORS: dict[Source, GeneratorBuilder] = {
    "marpower": _topic_generator(MarpowerGenerator),
    "sail_system": _topic_generator(SailSystemGenerator),
    "atpx": _atpx_generator,
}


async def _run_all_generators(
    mqtt_config: MQTTConfig,
    excluded_io_list_names: list[str] | None = None,
    cache_dir: Path | None = None,
):
    """Run all data generators concurrently."""
    excluded_set: set[str] = set(excluded_io_list_names or [])

    async with asyncio.TaskGroup() as tg:
        # NMEA is a fixed corpus, not io_list-driven, so it's started here
        # rather than dispatched via `_GENERATORS`.
        logger.info("Starting atpx_nmea generator")
        tg.create_task(AtpxNmeaGenerator(_PUBLISH_INTERVAL_SECONDS, mqtt_config).run())

        for source, file_names in io_lists:
            if source in excluded_set:
                logger.info(f"Skipping {source}; excluded by name")
                continue

            build = _GENERATORS.get(source)
            if build is None:
                logger.warning(f"No data generator found for source: {source}")
                continue

            paths = [Path(f"io_lists/{file_name}") for file_name in file_names]
            logger.debug(f"Processing {source} {paths}")

            io_result = read_io_list(paths, source, cache_dir=cache_dir)
            logger.info(f"Starting {source} generator")
            tg.create_task(
                build(_PUBLISH_INTERVAL_SECONDS, mqtt_config, io_result).run()
            )


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
