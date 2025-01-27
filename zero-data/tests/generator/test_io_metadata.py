from pathlib import Path, PosixPath
from unittest.mock import patch

import io_processing.generator.io_metadata as io_metadata

def test_io_metadata(marpower_normalized_df):

    with patch("polars.dataframe.DataFrame.write_csv", create=True) as mock_write_csv:
        io_metadata_df = io_metadata.IOMetadataWriter(Path("/not-used"), marpower_normalized_df).write_io_metadata_csv()
        mock_write_csv.assert_called_with(PosixPath("/not-used/seeds/io_metadata.csv"), quote_style='non_numeric')
        assert io_metadata_df.shape == (390,13)
