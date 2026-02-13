from pathlib import Path

from .marpower_raw import MarpowerRawGenerator
from .sail_system_raw import SailSystemRawGenerator
from .io_metadata import IOMetadataWriter
from .electrical_energy_metadata import MetadataGenerator
from zero_data.config import io_lists
from zero_data.io_list import read_io_list
from zero_data.io_list.readers.sail_system import read_sail_system
import logging

logger = logging.getLogger(__name__)


def generate_dbt():
    """Generate dbt models for all IO lists."""
    logger.info("Generating dbt models")
    dbt_path = Path("output")

    writer = IOMetadataWriter(dbt_path)
    dbt_generator = MarpowerRawGenerator(dbt_path)

    for source, file_names in io_lists:
        logger.debug(f"Processing {source} {file_names}")
        paths = [Path(f"io_lists/{file_name}") for file_name in file_names]
        io_result = read_io_list(paths, source)

        writer.write_io_metadata_csv(io_result.io_list, source)
        dbt_generator.generate(io_result.topics)

    sail_system_generator = SailSystemRawGenerator(dbt_path)
    sail_system_result = read_sail_system()
    sail_system_generator.generate(sail_system_result.topics)
    logger.info(f"Generated {len(sail_system_result.topics)} sail system source models")

    electrical_energy_metadata = MetadataGenerator(dbt_path)
    electrical_energy_metadata.generate()
