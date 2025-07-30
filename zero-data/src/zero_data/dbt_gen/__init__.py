from pathlib import Path

from .marpower_raw import MarpowerRawGenerator
from .io_metadata import IOMetadataWriter
from zero_data.config import io_lists
from zero_data.io_list import read_io_list
import logging

logger = logging.getLogger(__name__)


def generate_dbt():
    """Generate dbt models for all IO lists."""
    logger.info("Generating dbt models")
    dbt_path = Path("dbt")

    writer = IOMetadataWriter(dbt_path)
    dbt_generator = MarpowerRawGenerator(dbt_path)

    for source, file_name in io_lists:
        logger.debug(f"Processing {source} {file_name}")
        io_result = read_io_list(Path(f"io_lists/{file_name}"), source)

        writer.write_io_metadata_csv(io_result.io_list, source)
        dbt_generator.generate(io_result.topics)
