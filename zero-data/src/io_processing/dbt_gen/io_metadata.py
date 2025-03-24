from pathlib import PurePath, Path

from polars import DataFrame


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

    @staticmethod
    def clean_name(name: str) -> str:
        name_without_extension = PurePath(name).stem
        return str.lower(name_without_extension.replace(" ", "_").replace("/", "_"))

    def write_io_metadata_csv(self, df: DataFrame, name: str):
        name_clean = self.clean_name(name)
        metadata_path = self.dbt_path / f"seeds/io_metadata_{name_clean}.csv"
        df = df.select(*self.io_metadata_cols)
        df.write_csv(metadata_path, quote_style="non_numeric")
        print(f"Wrote {df.shape[0]} rows and {df.shape[1]} columns to {metadata_path}")
        return df
