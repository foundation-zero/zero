import polars as pl
import pytest

from sailpack.max_loads import (
    clamp_targets_to_thresholds,
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


def test_read_max_loads_converts_kilogram_to_tonne():
    max_loads_csv = (
        HEADER + ",,,,,,,\n"
        'main-sheet-load,E2.05,"12,800",,,"11,000","12,000",\n'
        'main-vang-load,2.02,"61,111","-20,000","-24,000","40,000","45,750",\n'
        "mizzen-halyard-load,E4.04,,,,2000,2500,\n"
        "staysail-sheet-ps-load,???,???,,,???,???,\n"
    )

    assert read_max_loads(max_loads_csv).to_dicts() == [
        _thresholds("main-sheet-load", warning_high=11.0, alarm_high=12.0),
        _thresholds("main-vang-load", -24.0, -20.0, 40.0, 45.75),
        _thresholds("mizzen-halyard-load", warning_high=2.0, alarm_high=2.5),
        _thresholds("staysail-sheet-ps-load"),
    ]


def test_read_max_loads_finds_columns_by_header():
    reordered_header = (
        ",,,,,\n"
        "Upper Alarm Setting (kg),Upper Warning Setting (kg),Lower Alarm Setting (kg),"
        "Lower Warning Setting (kg),Loads app technical name\n"
    )
    max_loads_csv = reordered_header + '"12,000","11,000",,,main-sheet-load\n'

    assert read_max_loads(max_loads_csv).to_dicts() == [
        _thresholds("main-sheet-load", warning_high=11.0, alarm_high=12.0)
    ]


def test_read_max_loads_rejects_missing_columns():
    header_without_lower_alarm = HEADER.replace("Lower Alarm Setting (kg)", "Notes")

    with pytest.raises(ValueError, match="Lower Alarm Setting"):
        read_max_loads(header_without_lower_alarm)


def test_read_max_loads_reads_missing_trailing_cells_as_empty():
    max_loads_csv = HEADER + "main-sheet-load,E2.05,,,,11000\n"

    assert read_max_loads(max_loads_csv).to_dicts() == [
        _thresholds("main-sheet-load", warning_high=11.0)
    ]


@pytest.mark.parametrize(
    "row",
    [
        'main-sheet-load,,,,,"13,000","12,000",\n',
        'main-vang-load,,,"-24,000","-20,000",,,\n',
        'main-sheet-load,,,"20,000",500,"11,000","12,000",\n',
        'main-sheet-load,,,,"13,000",,"12,000",\n',
    ],
)
def test_read_max_loads_rejects_thresholds_out_of_order(row: str):
    with pytest.raises(ValueError, match="-load"):
        read_max_loads(HEADER + row)


def test_clamp_targets_to_thresholds_clamps_to_the_warnings():
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

    targets, conflicts = clamp_targets_to_thresholds(reference_values, max_loads)

    assert conflicts.sort("sailpack_value").select(
        "Calculation ID", "tack", "sailpack_value", "value"
    ).rows() == [
        ("LC2", "port", 1.0, 2.0),
        ("LC2", "port", 11.5, 11.0),
    ]
    assert targets.sort("variable", "Calculation ID", "tack", "value").rows() == [
        ("LC1", "code-zero-tack-load", 30.0, "port"),
        ("LC1", "main-sheet-load", 10.0, "port"),
        ("LC2", "main-sheet-load", 2.0, "port"),
        ("LC2", "main-sheet-load", 11.0, "port"),
        ("LC2", "main-sheet-load", 9.0, "starboard"),
    ]


def test_clamp_targets_to_thresholds_clamps_to_the_alarm_without_a_warning():
    reference_values = pl.DataFrame(
        {
            "Calculation ID": ["LC1", "LC2"],
            "variable": ["main-outhaul-load", "main-vang-load"],
            "value": [15.0, -25.0],
            "tack": ["port", "port"],
        }
    )
    max_loads = pl.DataFrame(
        [
            _thresholds("main-outhaul-load", alarm_high=14.0),
            _thresholds("main-vang-load", alarm_low=-20.0),
        ],
        schema=THRESHOLDS_SCHEMA,
    )

    targets, conflicts = clamp_targets_to_thresholds(reference_values, max_loads)

    assert targets.sort("Calculation ID").rows() == [
        ("LC1", "main-outhaul-load", 14.0, "port"),
        ("LC2", "main-vang-load", -20.0, "port"),
    ]
    assert conflicts.height == 2


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
