from pathlib import Path
from typing import List

import pytest

from io_processing.io_list import IOTopic
from io_processing.io_list.marpower import (
    read_amcs_excel,
    normalize_amcs_io_list,
    io_topics,
)


@pytest.fixture
def marpower_normalized_df():
    repo_root = Path(__file__).parent / ".."
    amcs_df = read_amcs_excel(
        repo_root / "io_lists/52422003_3210_AMCS IO-List R1.11.xlsx"
    )
    return normalize_amcs_io_list(amcs_df)


@pytest.fixture
def marpower_io_topics(marpower_normalized_df) -> List[IOTopic]:
    return io_topics(marpower_normalized_df)
