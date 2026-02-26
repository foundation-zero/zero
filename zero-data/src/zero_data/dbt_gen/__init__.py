from pathlib import Path
from typing import Any

from .marpower_raw import MarpowerRawGenerator
from .sail_system_raw import SailSystemRawGenerator
from .io_metadata import IOMetadataWriter
from .electrical_energy_metadata import MetadataGenerator
from zero_data.config import io_lists
from zero_data.io_list import read_io_list, Source
import logging

logger = logging.getLogger(__name__)

_GENERATORS: dict[Source, Any] = {
    "marpower": MarpowerRawGenerator,
    "sail_system": SailSystemRawGenerator,
}


def generate_dbt():
    """Generate dbt models for all IO lists."""
    logger.info("Generating dbt models")
    dbt_path = Path("output")

    writer = IOMetadataWriter(dbt_path)

    for source, file_names in io_lists:
        logger.debug(f"Processing {source} {file_names}")
        paths = [Path(f"io_lists/{file_name}") for file_name in file_names]
        io_result = read_io_list(paths, source)

        # Not used right now but keeping it for backward compatibility
        if source == "marpower":
            writer.write_io_metadata_csv(io_result.io_list, source)
        dbt_generator_class = _GENERATORS[source]
        dbt_generator = dbt_generator_class(dbt_path)
        dbt_generator.generate(io_result.topics)

    electrical_energy_metadata = MetadataGenerator(dbt_path)
    electrical_energy_metadata.generate()
