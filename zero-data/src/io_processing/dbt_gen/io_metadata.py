from pathlib import Path

from polars import DataFrame
import logging

logger = logging.getLogger(__name__)


class IOMetadataWriter:
    def __init__(self, dbt_path: Path):
        self.dbt_path = dbt_path.resolve()
        self.io_metadata_cols = [
            "device",
            "tag",
            "yard_tag",
            "target_type",
            "module",
            "module_type",
            "terminal",
            "cabinet",
            "system",
            "description",
            "unit",
            "precision",
            "data_type",
        ]

    def write_io_metadata_csv(self, df: DataFrame, name: str):
        """Take the metadata columns of the IO List and write them to a CSV file."""
        metadata_path = self.dbt_path / f"seeds/io_metadata_{name}.csv"
        df = df.select(*self.io_metadata_cols)
        df.write_csv(metadata_path, quote_style="non_numeric")
        logger.info(
            f"Wrote {df.shape[0]} rows and {df.shape[1]} columns to {metadata_path}"
        )
        return df
