from pathlib import Path

from .marpower_raw import MarpowerRawGenerator
from .io_metadata import IOMetadataWriter
from io_processing.config import io_lists
from io_processing.io_list import read_io_list


def generate_dbt():
    dbt_path = Path("dbt/")

    writer = IOMetadataWriter(dbt_path)
    dbt_generator = MarpowerRawGenerator(dbt_path)

    for source, file_name in io_lists:
        io_result = read_io_list(Path(f"io_lists/{file_name}"), source)

        writer.write_io_metadata_csv(io_result.io_list, source)
        dbt_generator.generate(io_result.topics)
