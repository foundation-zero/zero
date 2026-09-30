from pathlib import Path

import polars as pl
import pytest

from sailpack.max_loads import (
    drop_targets_above_thresholds,
    read_max_loads,
    thresholded_variables,
)

HEADER = (
    ",,Equipment (Limiting) Specs,,,Relief Load Settings,,Alarms,,SailPack Modelling,,,\n"
    "Loads app technical name,Function #,Max Working Load (kg),Max Pull Setting (kg),"
    "Validation,Relief Load (kg),Validation,Warning Threshold (kg),Alarm Setting (kg),"
    "Max Working Load (kg),Cheat Sheet Ref Name,Validation,Additional Comments\n"
)


def _write_max_loads(tmp_path: Path, rows: str) -> Path:
    path = tmp_path / "max_loads.csv"
    path.write_text(HEADER + rows, encoding="utf-8")
    return path


def test_read_max_loads_converts_kilogram_to_tonne(tmp_path):
    path = _write_max_loads(
        tmp_path,
        ",,,,,,,,,,,,\n"
        'main-sheet-load,E2.05,"12,800",,,,,"11,000","12,000","11,700",LC5,,\n'
        "mizzen-halyard-load,E4.04,,,,,,2000,2500,n/a,,,\n"
        "staysail-sheet-ps-load,???,???,,???,???,???,???,???,,,,\n",
    )

    assert read_max_loads(path).to_dicts() == [
        {"variable": "main-sheet-load", "warning_high": 11.0, "alarm_high": 12.0},
        {"variable": "mizzen-halyard-load", "warning_high": 2.0, "alarm_high": 2.5},
        {
            "variable": "staysail-sheet-ps-load",
            "warning_high": None,
            "alarm_high": None,
        },
    ]


def test_read_max_loads_rejects_warning_above_alarm(tmp_path):
    path = _write_max_loads(tmp_path, 'main-sheet-load,,,,,,,"13,000","12,000",,,,\n')

    with pytest.raises(ValueError, match="main-sheet-load"):
        read_max_loads(path)


def test_drop_targets_above_thresholds():
    reference_values = pl.DataFrame(
        {
            "Calculation ID": ["LC1", "LC2", "LC1", "LC2", "LC1"],
            "variable": ["main-sheet-load"] * 4 + ["code-zero-tack-load"],
            "value": [10.0, 11.5, None, 9.0, 30.0],
            "tack": ["port", "port", "starboard", "starboard", "port"],
        }
    )
    max_loads = pl.DataFrame(
        {
            "variable": ["main-sheet-load"],
            "warning_high": [11.0],
            "alarm_high": [12.0],
        }
    )

    targets, conflicts = drop_targets_above_thresholds(reference_values, max_loads)

    assert conflicts.select("Calculation ID", "tack", "value").to_dicts() == [
        {"Calculation ID": "LC2", "tack": "port", "value": 11.5}
    ]
    assert targets.sort("variable", "Calculation ID", "tack").rows() == [
        ("LC1", "code-zero-tack-load", 30.0, "port"),
        ("LC1", "main-sheet-load", 10.0, "port"),
        ("LC2", "main-sheet-load", 9.0, "starboard"),
    ]


def test_thresholded_variables_skips_variables_without_thresholds():
    max_loads = pl.DataFrame(
        {
            "variable": ["main-sheet-load", "a2-tack-load", "main-outhaul-load"],
            "warning_high": [11.0, None, None],
            "alarm_high": [12.0, None, 14.0],
        }
    )

    assert thresholded_variables(max_loads)["variable"].to_list() == [
        "main-sheet-load",
        "main-outhaul-load",
    ]
