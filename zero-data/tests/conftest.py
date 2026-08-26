from pathlib import Path

import pytest
from polars import DataFrame

from zero_data.io_list import IOResult, read_io_list


@pytest.fixture
def marpower_io_result() -> IOResult:
    return read_io_list(
        [(Path(__file__).parent / "../io_lists/test/marpower_test.xlsx")], "marpower"
    )


@pytest.fixture
def marpower_io_list(marpower_io_result: IOResult) -> DataFrame:
    return marpower_io_result.io_list
