from pathlib import Path

import pytest

from loads.registry.sheets import (
    TABS,
    VITTERS_JOIN_PATH,
    max_loads_problems,
    unknown_technical_names,
    unresolved_vitters_joins,
)


@pytest.mark.parametrize(
    ("path", "header_rows"),
    [
        (TABS["sailpack-mapping"].path, TABS["sailpack-mapping"].header_rows),
        (TABS["max-loads"].path, TABS["max-loads"].header_rows),
        (VITTERS_JOIN_PATH, 1),
    ],
)
def test_sheet_technical_names_are_in_registry(path: Path, header_rows: int):
    assert unknown_technical_names(path, header_rows) == set()


def test_vitters_join_resolves_to_io_list():
    assert unresolved_vitters_joins() == []


def test_max_loads_parse():
    assert max_loads_problems() == []
