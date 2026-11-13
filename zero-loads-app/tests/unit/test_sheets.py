import pytest

from loads.registry.sheets import (
    first_column_values,
    max_loads_problems,
    max_loads_technical_names,
    sailpack_mapping_problems,
)

MAX_LOADS_HEADER = (
    ",,Alarms,,,,Function\n"
    "Loads app technical name,Lower Warning Setting (kg),Lower Alarm Setting (kg),"
    "Upper Warning Setting (kg),Upper Alarm Setting (kg),PLC reference\n"
)

SAILPACK_MAPPING_HEADER = (
    "Technical name,Sailpack table name,Sailpack row label,Sailpack column label,"
    "Purchase (sailpack : function)\n"
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
        "Lower Warning Setting (kg),Loads app technical name,PLC reference\n"
    )
    max_loads_csv = reordered_header + '"12,000","11,000",,,main-sheet-load,\n'

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


def test_sailpack_mapping_problems_report_mapped_loads_without_a_purchase():
    mapping_csv = (
        f"{SAILPACK_MAPPING_HEADER}"
        "main-sheet-load,CABLE DATA,CABLE_MAINSHEET,Load (N),2\n"
        "main-vang-load,CABLE DATA,CABLE_VANG,Load (N),\n"
        "main-outhaul-load,CABLE DATA,CABLE_MAIN_OUTHAUL,Load (N),n/a\n"
        "main-vang-relative-position,CABLE DATA,CABLE_VANG,Unloaded length (m) - After FSIC,\n"
        "main-halyard-load,,,,\n"
    )

    assert sailpack_mapping_problems(mapping_csv) == [
        "SailPack mapping: main-vang-load (CABLE_VANG) has no numeric purchase",
        "SailPack mapping: main-outhaul-load (CABLE_MAIN_OUTHAUL) has no numeric purchase",
    ]


def test_sailpack_mapping_problems_report_a_missing_purchase_column():
    mapping_csv = (
        "Technical name,Sailpack table name,Sailpack row label,Sailpack column label\n"
    )

    assert sailpack_mapping_problems(mapping_csv) == [
        "SailPack mapping: Column not found in the SailPack mapping: "
        "Purchase (sailpack : function)"
    ]
