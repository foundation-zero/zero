import csv
from pathlib import Path

import pytest

from loads.registry import VARIABLES

SRC = Path(__file__).parents[2] / "src"


def _technical_names(path: Path, header_rows: int) -> set[str]:
    with path.open(newline="") as file:
        rows = list(csv.reader(file))[header_rows:]
    return {row[0] for row in rows if row and row[0]}


@pytest.mark.parametrize(
    ("path", "header_rows"),
    [
        (SRC / "loads" / "registry" / "max_loads.csv", 2),
        (SRC / "loads" / "registry" / "vitters_join.csv", 1),
        (SRC / "sailpack" / "sailpack_mapping.csv", 1),
    ],
)
def test_sheet_technical_names_are_in_registry(path: Path, header_rows: int):
    assert _technical_names(path, header_rows) - VARIABLES.keys() == set()
