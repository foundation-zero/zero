import csv
import io
from itertools import combinations
from pathlib import Path

import polars as pl

from sailpack.seed_utils import RUNNER_BLOCK_LOAD_PER_TAIL_LOAD, mirror_side

KILOGRAM_PER_TONNE = 1000.0

# The "Max loads" tab export has a row of column groups above the column headers.
MAX_LOADS_HEADER_ROWS = 2
TECHNICAL_NAME_HEADER = "Loads app technical name"
THRESHOLD_HEADERS = {
    "alarm_low": "Lower Alarm Setting (kg)",
    "warning_low": "Lower Warning Setting (kg)",
    "warning_high": "Upper Warning Setting (kg)",
    "alarm_high": "Upper Alarm Setting (kg)",
}
THRESHOLD_COLUMNS = list(THRESHOLD_HEADERS)


def kilogram_to_tonne(cell: str) -> float | None:
    try:
        return float(cell.replace(",", "").strip()) / KILOGRAM_PER_TONNE
    except ValueError:
        return None


def read_max_loads_cells(max_loads_csv: str) -> list[dict[str, str]]:
    """Return the technical name and raw threshold cells of every named row."""
    rows = list(csv.reader(io.StringIO(max_loads_csv, newline="")))

    headers = [header.strip() for header in rows[MAX_LOADS_HEADER_ROWS - 1]]
    missing_headers = [
        header
        for header in [TECHNICAL_NAME_HEADER, *THRESHOLD_HEADERS.values()]
        if header not in headers
    ]
    if missing_headers:
        raise ValueError(f"Columns not found in the max loads: {missing_headers}")

    column_positions = {
        "variable": headers.index(TECHNICAL_NAME_HEADER),
        **{
            column: headers.index(header)
            for column, header in THRESHOLD_HEADERS.items()
        },
    }
    padded_rows = [
        [*row, *[""] * (len(headers) - len(row))]
        for row in rows[MAX_LOADS_HEADER_ROWS:]
    ]
    return [
        {column: row[position].strip() for column, position in column_positions.items()}
        for row in padded_rows
        if row[column_positions["variable"]].strip()
    ]


def runner_block_thresholds(max_loads: pl.DataFrame) -> pl.DataFrame:
    """Derive the runner block thresholds on both sides from the runner tail thresholds."""
    block_load_per_tail_load = pl.DataFrame(
        [
            {"block": side_block, "variable": side_tail, "factor": factor}
            for (block, tail), factor in RUNNER_BLOCK_LOAD_PER_TAIL_LOAD.items()
            for side_block, side_tail in [
                (block, tail),
                (mirror_side(block), mirror_side(tail)),
            ]
        ]
    )
    return max_loads.join(block_load_per_tail_load, on="variable").select(
        pl.col("block").alias("variable"),
        *(pl.col(column) * pl.col("factor") for column in THRESHOLD_COLUMNS),
    )


def read_max_loads(max_loads_csv: str) -> pl.DataFrame:
    """Read the max loads in tonnes, including the runner block thresholds derived from the tails."""
    sheet_max_loads = pl.DataFrame(
        [
            {
                "variable": cells["variable"],
                **{
                    column: kilogram_to_tonne(cells[column])
                    for column in THRESHOLD_COLUMNS
                },
            }
            for cells in read_max_loads_cells(max_loads_csv)
        ],
        schema={
            "variable": pl.String,
            **{column: pl.Float64 for column in THRESHOLD_COLUMNS},
        },
    )
    max_loads = pl.concat([sheet_max_loads, runner_block_thresholds(sheet_max_loads)])

    out_of_order = max_loads.filter(
        pl.any_horizontal(
            (pl.col(lower) > pl.col(higher)).fill_null(False)
            for lower, higher in combinations(THRESHOLD_COLUMNS, 2)
        )
    )
    if not out_of_order.is_empty():
        raise ValueError(
            "Thresholds not in the order alarm_low ≤ warning_low ≤ warning_high ≤ alarm_high "
            f"in max loads: {out_of_order.to_dicts()}"
        )

    duplicates = max_loads.filter(pl.col("variable").is_duplicated())
    if not duplicates.is_empty():
        raise ValueError(
            f"Duplicate technical names in max loads: {duplicates['variable'].unique().to_list()}"
        )

    return max_loads


def drop_targets_outside_thresholds(
    reference_values: pl.DataFrame, max_loads: pl.DataFrame
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Split the SailPack targets into those within their thresholds and the conflicts.

    The API falls back to the thresholds wherever a reference value has none, so a target
    outside them would show beyond its own warning or alarm.
    """
    targets = reference_values.filter(pl.col("value").is_not_null()).join(
        max_loads, on="variable", how="left"
    )
    outside_thresholds = pl.any_horizontal(
        (pl.col("value") < pl.col("alarm_low")).fill_null(False),
        (pl.col("value") < pl.col("warning_low")).fill_null(False),
        (pl.col("value") > pl.col("warning_high")).fill_null(False),
        (pl.col("value") > pl.col("alarm_high")).fill_null(False),
    )

    conflicts = targets.filter(outside_thresholds).sort(
        "variable", "Calculation ID", "tack"
    )
    targets_within_thresholds = targets.filter(~outside_thresholds).select(
        "Calculation ID", "variable", "value", "tack"
    )

    return targets_within_thresholds, conflicts


def thresholded_variables(max_loads: pl.DataFrame) -> pl.DataFrame:
    return max_loads.filter(
        pl.any_horizontal(pl.col(column).is_not_null() for column in THRESHOLD_COLUMNS)
    )


def write_conflicts(conflicts: pl.DataFrame, output_csv: Path) -> None:
    conflicts.select(
        pl.col("variable").alias("technical_name"),
        pl.col("Calculation ID").alias("load_case_id"),
        "tack",
        pl.col("value").round(3).alias("dropped_target"),
        *THRESHOLD_COLUMNS,
    ).write_csv(output_csv)
