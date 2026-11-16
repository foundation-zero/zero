import csv
import io
from itertools import combinations
from pathlib import Path

import polars as pl

KILOGRAM_PER_TONNE = 1000.0

# The "Max loads" tab export has a row of column groups above the column headers.
MAX_LOADS_HEADER_ROWS = 2
TECHNICAL_NAME_HEADER = "Loads app technical name"
PLC_REFERENCE_HEADER = "PLC reference"
THRESHOLD_HEADERS = {
    "alarm_low": "Lower Alarm Setting (kg)",
    "warning_low": "Lower Warning Setting (kg)",
    "warning_high": "Upper Warning Setting (kg)",
    "alarm_high": "Upper Alarm Setting (kg)",
}
THRESHOLD_COLUMNS = list(THRESHOLD_HEADERS)

# TODO: Read these rows once the team has settled them: the reef tacks have no PLC reference yet,
# and the sheet line loads share their technical name with the sheet block loads.
IGNORED_ROWS = {
    ("main-reef-tack", ""),
    ("mizzen-reef-tack", ""),
    ("main-sheet-load", "FE205_MainSheetCaptiveWinch.st_load.i_Load"),
    ("mizzen-sheet-load", "FE504_MizzenSheetCaptiveWinch.st_load.i_Load"),
}


def kilogram_to_tonne(cell: str) -> float | None:
    try:
        return float(cell.replace(",", "").strip()) / KILOGRAM_PER_TONNE
    except ValueError:
        return None


def read_max_loads_cells(max_loads_csv: str) -> list[dict[str, str]]:
    """Return the technical name, PLC reference and raw threshold cells of every named row."""
    rows = list(csv.reader(io.StringIO(max_loads_csv, newline="")))

    headers = [header.strip() for header in rows[MAX_LOADS_HEADER_ROWS - 1]]
    missing_headers = [
        header
        for header in [
            TECHNICAL_NAME_HEADER,
            PLC_REFERENCE_HEADER,
            *THRESHOLD_HEADERS.values(),
        ]
        if header not in headers
    ]
    if missing_headers:
        raise ValueError(f"Columns not found in the max loads: {missing_headers}")

    column_positions = {
        "variable": headers.index(TECHNICAL_NAME_HEADER),
        "plc_reference": headers.index(PLC_REFERENCE_HEADER),
        **{
            column: headers.index(header)
            for column, header in THRESHOLD_HEADERS.items()
        },
    }
    padded_rows = [
        [*row, *[""] * (len(headers) - len(row))]
        for row in rows[MAX_LOADS_HEADER_ROWS:]
    ]
    named_rows = [
        {column: row[position].strip() for column, position in column_positions.items()}
        for row in padded_rows
        if row[column_positions["variable"]].strip()
    ]
    return [
        cells
        for cells in named_rows
        if (cells["variable"], cells["plc_reference"]) not in IGNORED_ROWS
    ]


def read_max_loads(max_loads_csv: str) -> pl.DataFrame:
    """Read the max loads in tonnes."""
    max_loads = pl.DataFrame(
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


def clamp_targets_to_thresholds(
    reference_values: pl.DataFrame, max_loads: pl.DataFrame
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Clamp the SailPack targets to their warnings, or alarms where a side has no warning.

    The API falls back to the thresholds wherever a reference value has none, so a target
    outside them would show beyond its own warning or alarm. Returns the targets and the
    conflicts, the targets that were clamped.
    """
    targets = (
        reference_values.filter(pl.col("value").is_not_null())
        .join(max_loads, on="variable", how="left")
        .rename({"value": "sailpack_value"})
        .with_columns(
            pl.col("sailpack_value")
            .clip(
                pl.coalesce("warning_low", "alarm_low"),
                pl.coalesce("warning_high", "alarm_high"),
            )
            .alias("value")
        )
    )

    conflicts = targets.filter(pl.col("value") != pl.col("sailpack_value")).sort(
        "variable", "Calculation ID", "tack"
    )
    clamped_targets = targets.select("Calculation ID", "variable", "value", "tack")

    return clamped_targets, conflicts


def thresholded_variables(max_loads: pl.DataFrame) -> pl.DataFrame:
    return max_loads.filter(
        pl.any_horizontal(pl.col(column).is_not_null() for column in THRESHOLD_COLUMNS)
    )


def write_conflicts(conflicts: pl.DataFrame, output_csv: Path) -> None:
    conflicts.select(
        pl.col("variable").alias("technical_name"),
        pl.col("Calculation ID").alias("load_case_id"),
        "tack",
        pl.col("sailpack_value").round(3).alias("sailpack_target"),
        pl.col("value").round(3).alias("seeded_target"),
        *THRESHOLD_COLUMNS,
    ).write_csv(output_csv)
