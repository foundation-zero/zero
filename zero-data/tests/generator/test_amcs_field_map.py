from pathlib import Path, PosixPath
from unittest.mock import patch, mock_open

import io_processing.generator.amcs_field_map


def test_amcs_field_map(marpower_io_values):

    open_mock = mock_open()
    with patch("io_processing.generator.amcs_field_map.open", open_mock, create=True):
        macro = io_processing.generator.amcs_field_map.AMCSFieldMapCTEGenerator(marpower_io_values, Path("/not-used")).generate()
        open_mock.assert_called_with(PosixPath("/not-used/models/raw/amcs_cte.sql"), "w")
        assert macro is not None
