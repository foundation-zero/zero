from pathlib import Path

from io_processing.generator.io_metadata import IOMetadataWriter
from io_processing.generator.marpower_raw import MarpowerRawGenerator
from io_processing.io_list.marpower import (
    read_amcs_excel,
    normalize_amcs_io_list,
    io_topics,
)


def generate():
    repo_root = Path(__file__).parent / "../../.."
    dbt_path = repo_root / "dbt"
    amcs_df = read_amcs_excel(
        repo_root / "io_lists/52422003_3210_AMCS IO-List R1.11.xlsx"
    )
    normalized_df = normalize_amcs_io_list(amcs_df)
    topics = io_topics(normalized_df)

    IOMetadataWriter(dbt_path, normalized_df).write_io_metadata_csv()
    MarpowerRawGenerator(dbt_path, topics).generate()
