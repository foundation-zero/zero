from pathlib import Path

import polars as pl
import pytest

from sailpack.max_loads import (
    drop_targets_outside_thresholds,
    read_max_loads,
    runner_block_thresholds,
    thresholded_variables,
)

HEADER = (
    ",,Equipment (Limiting) Specs,,Alarms,,,\n"
    "Loads app technical name,Function #,Max Working Load (kg),"
    "Lower Warning Setting (kg),Lower Alarm Setting (kg),"
    "Upper Warning Setting (kg),Upper Alarm Setting (kg),Additional Comments\n"
)


THRESHOLDS_SCHEMA = {
    "variable": pl.String,
    "alarm_low": pl.Float64,
    "warning_low": pl.Float64,
    "warning_high": pl.Float64,
    "alarm_high": pl.Float64,
}


def _write_max_loads(tmp_path: Path, header: str, rows: str) -> Path:
    path = tmp_path / "max_loads.csv"
    path.write_text(header + rows, encoding="utf-8")
    return path


def _thresholds(
    variable: str,
    alarm_low: float | None = None,
    warning_low: float | None = None,
    warning_high: float | None = None,
    alarm_high: float | None = None,
) -> dict[str, str | float | None]:
    return {
        "variable": variable,
        "alarm_low": alarm_low,
        "warning_low": warning_low,
        "warning_high": warning_high,
        "alarm_high": alarm_high,
    }


def test_read_max_loads_converts_kilogram_to_tonne(tmp_path):
    path = _write_max_loads(
        tmp_path,
        HEADER,
        ",,,,,,,\n"
        'main-sheet-load,E2.05,"12,800",,,"11,000","12,000",\n'
        'main-vang-load,2.02,"61,111","-20,000","-24,000","40,000","45,750",\n'
        "mizzen-halyard-load,E4.04,,,,2000,2500,\n"
        "staysail-sheet-ps-load,???,???,,,???,???,\n",
    )

    assert read_max_loads(path).to_dicts() == [
        _thresholds("main-sheet-load", warning_high=11.0, alarm_high=12.0),
        _thresholds("main-vang-load", -24.0, -20.0, 40.0, 45.75),
        _thresholds("mizzen-halyard-load", warning_high=2.0, alarm_high=2.5),
        _thresholds("staysail-sheet-ps-load"),
    ]


def test_read_max_loads_finds_columns_by_header(tmp_path):
    reordered_header = (
        ",,,,,\n"
        "Upper Alarm Setting (kg),Upper Warning Setting (kg),Lower Alarm Setting (kg),"
        "Lower Warning Setting (kg),Loads app technical name\n"
    )
    path = _write_max_loads(
        tmp_path, reordered_header, '"12,000","11,000",,,main-sheet-load\n'
    )

    assert read_max_loads(path).to_dicts() == [
        _thresholds("main-sheet-load", warning_high=11.0, alarm_high=12.0)
    ]


def test_read_max_loads_rejects_missing_columns(tmp_path):
    header_without_lower_alarm = HEADER.replace("Lower Alarm Setting (kg)", "Notes")
    path = _write_max_loads(tmp_path, header_without_lower_alarm, "")

    with pytest.raises(ValueError, match="Lower Alarm Setting"):
        read_max_loads(path)


@pytest.mark.parametrize(
    "row",
    [
        'main-sheet-load,,,,,"13,000","12,000",\n',
        'main-vang-load,,,"-24,000","-20,000",,,\n',
    ],
)
def test_read_max_loads_rejects_thresholds_out_of_order(tmp_path, row: str):
    path = _write_max_loads(tmp_path, HEADER, row)

    with pytest.raises(ValueError, match="-load"):
        read_max_loads(path)


def test_drop_targets_outside_thresholds():
    reference_values = pl.DataFrame(
        {
            "Calculation ID": ["LC1", "LC2", "LC1", "LC2", "LC1", "LC2"],
            "variable": ["main-sheet-load"] * 4
            + ["code-zero-tack-load", "main-sheet-load"],
            "value": [10.0, 11.5, None, 9.0, 30.0, 1.0],
            "tack": ["port", "port", "starboard", "starboard", "port", "port"],
        }
    )
    max_loads = pl.DataFrame(
        [_thresholds("main-sheet-load", 0.5, 2.0, 11.0, 12.0)],
        schema=THRESHOLDS_SCHEMA,
    )

    targets, conflicts = drop_targets_outside_thresholds(reference_values, max_loads)

    assert conflicts.sort("value").select(
        "Calculation ID", "tack", "value"
    ).to_dicts() == [
        {"Calculation ID": "LC2", "tack": "port", "value": 1.0},
        {"Calculation ID": "LC2", "tack": "port", "value": 11.5},
    ]
    assert targets.sort("variable", "Calculation ID", "tack").rows() == [
        ("LC1", "code-zero-tack-load", 30.0, "port"),
        ("LC1", "main-sheet-load", 10.0, "port"),
        ("LC2", "main-sheet-load", 9.0, "starboard"),
    ]


def test_thresholded_variables_skips_variables_without_thresholds():
    max_loads = pl.DataFrame(
        [
            _thresholds("main-sheet-load", warning_high=11.0, alarm_high=12.0),
            _thresholds("a2-tack-load"),
            _thresholds("main-outhaul-load", alarm_high=14.0),
            _thresholds("main-vang-load", warning_low=-20.0),
        ]
    )

    assert thresholded_variables(max_loads)["variable"].to_list() == [
        "main-sheet-load",
        "main-outhaul-load",
        "main-vang-load",
    ]


def test_runner_block_thresholds_scale_the_runner_tail_thresholds_on_both_sides():
    max_loads = pl.DataFrame(
        [
            _thresholds("main-runner-tail-ps-load", warning_high=13.0, alarm_high=14.0),
            _thresholds("main-runner-tail-sb-load", warning_high=13.0, alarm_high=14.0),
            _thresholds("mizzen-runner-tail-ps-load", warning_high=5.0, alarm_high=5.5),
            _thresholds("mizzen-runner-tail-sb-load", warning_high=5.0, alarm_high=5.5),
            _thresholds("main-sheet-load", warning_high=11.0, alarm_high=12.0),
        ],
        schema=THRESHOLDS_SCHEMA,
    )

    block_thresholds = {
        row["variable"]: (row["warning_high"], row["alarm_high"])
        for row in runner_block_thresholds(max_loads).iter_rows(named=True)
    }

    assert block_thresholds == {
        "main-runner-block-ps-load": (26.0, 28.0),
        "main-runner-block-sb-load": (26.0, 28.0),
        "mizzen-runner-block-ps-load": pytest.approx((9.563, 10.519), abs=1e-3),
        "mizzen-runner-block-sb-load": pytest.approx((9.563, 10.519), abs=1e-3),
    }
