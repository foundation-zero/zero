from pathlib import Path

import polars as pl
import pytest

from sailpack.max_loads import apply_max_loads, read_max_loads

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


def test_apply_max_loads_drops_targets_above_thresholds():
    reference_values = pl.DataFrame(
        {
            "Calculation ID": ["LC1", "LC2", "LC1", "LC2"],
            "variable": ["main-sheet-load"] * 4,
            "value": [10.0, 11.5, None, 9.0],
            "tack": ["port", "port", "starboard", "starboard"],
        }
    )
    max_loads = pl.DataFrame(
        {
            "variable": ["main-sheet-load", "primary-winch-ps-load", "a2-tack-load"],
            "warning_high": [11.0, 11.5, None],
            "alarm_high": [12.0, 12.5, None],
        }
    )

    reference_values_with_thresholds, conflicts = apply_max_loads(
        reference_values, max_loads
    )

    assert conflicts.select("Calculation ID", "tack", "value").to_dicts() == [
        {"Calculation ID": "LC2", "tack": "port", "value": 11.5}
    ]
    assert reference_values_with_thresholds.sort(
        "variable", "Calculation ID", "tack"
    ).to_dicts() == [
        {
            "Calculation ID": calculation_id,
            "variable": variable,
            "value": value,
            "tack": tack,
            "warning_high": warning_high,
            "alarm_high": alarm_high,
        }
        for variable, calculation_id, tack, value, warning_high, alarm_high in [
            ("main-sheet-load", "LC1", "port", 10.0, 11.0, 12.0),
            ("main-sheet-load", "LC1", "starboard", None, 11.0, 12.0),
            ("main-sheet-load", "LC2", "port", None, 11.0, 12.0),
            ("main-sheet-load", "LC2", "starboard", 9.0, 11.0, 12.0),
            ("primary-winch-ps-load", "LC1", "port", None, 11.5, 12.5),
            ("primary-winch-ps-load", "LC1", "starboard", None, 11.5, 12.5),
            ("primary-winch-ps-load", "LC2", "port", None, 11.5, 12.5),
            ("primary-winch-ps-load", "LC2", "starboard", None, 11.5, 12.5),
        ]
    ]


def test_apply_max_loads_adds_thresholds_to_tacks_without_a_target():
    reference_values = pl.DataFrame(
        {
            "Calculation ID": ["LC1", "LC1"],
            "variable": ["primary-winch-sb-load", "primary-winch-ps-load"],
            "value": [9.0, 9.0],
            "tack": ["port", "starboard"],
        }
    )
    max_loads = pl.DataFrame(
        {
            "variable": ["primary-winch-ps-load", "primary-winch-sb-load"],
            "warning_high": [11.5, 11.5],
            "alarm_high": [12.5, 12.5],
        }
    )

    reference_values_with_thresholds, _ = apply_max_loads(reference_values, max_loads)

    assert reference_values_with_thresholds.sort("variable", "tack").select(
        "variable", "tack", "value", "alarm_high"
    ).rows() == [
        ("primary-winch-ps-load", "port", None, 12.5),
        ("primary-winch-ps-load", "starboard", 9.0, 12.5),
        ("primary-winch-sb-load", "port", 9.0, 12.5),
        ("primary-winch-sb-load", "starboard", None, 12.5),
    ]
