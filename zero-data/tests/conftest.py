from typing import List

import pytest
from io_processing.io_list.types import IOTopic
from io_processing.io_list import read_io_list
from polars import DataFrame
from pathlib import Path

io_result = read_io_list(Path("io_lists/test/marpower_test.xlsx"), "marpower")


@pytest.fixture
def marpower_io_list() -> DataFrame:
    return io_result.io_list


@pytest.fixture
def marpower_io_topics() -> List[IOTopic]:
    return io_result.topics
