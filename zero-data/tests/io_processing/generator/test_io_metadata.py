from pathlib import Path, PosixPath
from unittest.mock import patch

from io_processing.dbt_gen.io_metadata import IOMetadataWriter


def test_io_metadata(marpower_io_list):
    with patch("polars.dataframe.DataFrame.write_csv", create=True) as mock_write_csv:
        io_metadata_df = IOMetadataWriter(Path("/not-used")).write_io_metadata_csv(
            marpower_io_list, "marpower"
        )
        mock_write_csv.assert_called_with(
            PosixPath("/not-used/seeds/io_metadata_marpower.csv"),
            quote_style="non_numeric",
        )
        assert io_metadata_df.shape == (390, 13)
