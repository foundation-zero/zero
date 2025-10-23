import pytest
from zero_data.io_list import read_io_list, IOResult
from polars import DataFrame
from pathlib import Path


@pytest.fixture
def marpower_io_result() -> IOResult:
    return read_io_list(
        [(Path(__file__).parent / "../io_lists/test/marpower_test.xlsx")], "marpower"
    )


@pytest.fixture
def marpower_io_list(marpower_io_result: IOResult) -> DataFrame:
    return marpower_io_result.io_list
