import pytest

from loads.registry.sheets import (
    first_column_values,
    max_loads_problems,
    max_loads_technical_names,
)

MAX_LOADS_HEADER = (
    ",,Alarms,,,\n"
    "Loads app technical name,Lower Warning Setting (kg),Lower Alarm Setting (kg),"
    "Upper Warning Setting (kg),Upper Alarm Setting (kg)\n"
)


def test_first_column_values_skips_the_header_rows_and_blank_names():
    csv_text = (
        "Loads app technical name,Note\n"
        "main-sheet-load,\n"
        ",a row without a technical name\n"
        "main-sheet-lod,\n"
    )

    assert first_column_values(csv_text, header_rows=1) == {
        "main-sheet-load",
        "main-sheet-lod",
    }


def test_max_loads_technical_names_finds_the_column_by_header():
    reordered_header = (
        ",,,,,\n"
        "Upper Alarm Setting (kg),Upper Warning Setting (kg),Lower Alarm Setting (kg),"
        "Lower Warning Setting (kg),Loads app technical name\n"
    )
    max_loads_csv = reordered_header + '"12,000","11,000",,,main-sheet-load\n'

    assert max_loads_technical_names(max_loads_csv) == {"main-sheet-load"}


@pytest.mark.parametrize(
    ("row", "problem"),
    [
        ('main-sheet-load,,,"11,000","12,000"\n', None),
        ("main-sheet-load,,,???,n/a\n", None),
        ('main-vang-load,"-20,000","-24,000",,\n', None),
        ("main-sheet-load,,,11000\n", None),
        ("main-sheet-load,,,11 t,12000\n", "non-numeric warning_high"),
        ('main-sheet-load,,,"13,000","12,000"\n', "not in the order"),
    ],
)
def test_max_loads_problems(row: str, problem: str | None):
    problems = max_loads_problems(MAX_LOADS_HEADER + row)

    if problem is None:
        assert problems == []
    else:
        assert any(problem.lower() in found.lower() for found in problems), problems
