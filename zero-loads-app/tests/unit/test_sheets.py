from pathlib import Path

import pytest

from loads.registry.sheets import (
    TABS,
    IoListLabel,
    io_list_labels,
    io_list_topics_without_variable,
    max_loads_problems,
    stale_io_list_exceptions,
    unknown_technical_names,
)


@pytest.mark.parametrize(
    ("path", "header_rows"),
    [
        (TABS["sailpack-mapping"].path, TABS["sailpack-mapping"].header_rows),
        (TABS["max-loads"].path, TABS["max-loads"].header_rows),
    ],
)
def test_sheet_technical_names_are_in_registry(path: Path, header_rows: int):
    assert unknown_technical_names(path, header_rows) == set()


def test_io_list_display_names_match_a_registry_variable():
    assert io_list_topics_without_variable() == []


def test_io_list_exceptions_are_labelled_topics_outside_the_registry():
    assert stale_io_list_exceptions() == []


def test_io_list_labels_join_on_topic_regardless_of_case():
    labels = io_list_labels()

    assert labels["blade-adjuster-load"] == IoListLabel(
        display_name="Blade RTA Load",
        abbreviated_display_name="B RTA",
        display_units="t",
    )
    assert labels["mast-lock-main-1"].display_name == "Main Reef 1 lock"


def test_max_loads_parse():
    assert max_loads_problems() == []
