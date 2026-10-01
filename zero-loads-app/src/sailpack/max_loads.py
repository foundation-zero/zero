import csv
from pathlib import Path

import polars as pl

KILOGRAM_PER_TONNE = 1000.0

# Column positions in the "Max loads" tab export, which has two header rows.
HEADER_ROWS = 2
TECHNICAL_NAME_COLUMN = 0
WARNING_THRESHOLD_COLUMN = 7
ALARM_SETTING_COLUMN = 8


def _kilogram_to_tonne(cell: str) -> float | None:
    try:
        return float(cell.replace(",", "").strip()) / KILOGRAM_PER_TONNE
    except ValueError:
        return None


def read_max_loads(max_loads_path: Path) -> pl.DataFrame:
    if not max_loads_path.exists():
        raise FileNotFoundError(f"Max loads file not found: {max_loads_path}")

    with max_loads_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))[HEADER_ROWS:]

    max_loads = pl.DataFrame(
        [
            {
                "variable": row[TECHNICAL_NAME_COLUMN].strip(),
                "warning_high": _kilogram_to_tonne(row[WARNING_THRESHOLD_COLUMN]),
                "alarm_high": _kilogram_to_tonne(row[ALARM_SETTING_COLUMN]),
            }
            for row in rows
            if row and row[TECHNICAL_NAME_COLUMN].strip()
        ],
        schema={
            "variable": pl.String,
            "warning_high": pl.Float64,
            "alarm_high": pl.Float64,
        },
    )

    warning_above_alarm = max_loads.filter(
        pl.col("warning_high") > pl.col("alarm_high")
    )
    if not warning_above_alarm.is_empty():
        raise ValueError(
            "Warning threshold above alarm setting in max loads: "
            f"{warning_above_alarm.to_dicts()}"
        )

    duplicates = max_loads.filter(pl.col("variable").is_duplicated())
    if not duplicates.is_empty():
        raise ValueError(
            f"Duplicate technical names in max loads: {duplicates['variable'].unique().to_list()}"
        )

    return max_loads


def drop_targets_above_thresholds(
    reference_values: pl.DataFrame, max_loads: pl.DataFrame
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Split the SailPack targets into those within their max thresholds and the conflicts.

    The API falls back to the max thresholds wherever a reference value has none, so a target
    above them would show above its own warning or alarm.
    """
    targets = reference_values.filter(pl.col("value").is_not_null()).join(
        max_loads, on="variable", how="left"
    )
    exceeds_threshold = (pl.col("value") > pl.col("warning_high")).fill_null(False) | (
        pl.col("value") > pl.col("alarm_high")
    ).fill_null(False)

    conflicts = targets.filter(exceeds_threshold).sort(
        "variable", "Calculation ID", "tack"
    )
    targets_within_thresholds = targets.filter(~exceeds_threshold).select(
        "Calculation ID", "variable", "value", "tack"
    )

    return targets_within_thresholds, conflicts


def thresholded_variables(max_loads: pl.DataFrame) -> pl.DataFrame:
    return max_loads.filter(
        pl.col("warning_high").is_not_null() | pl.col("alarm_high").is_not_null()
    )


def write_conflicts(conflicts: pl.DataFrame, output_csv: Path) -> None:
    conflicts.select(
        pl.col("variable").alias("technical_name"),
        pl.col("Calculation ID").alias("load_case_id"),
        "tack",
        pl.col("value").round(3).alias("dropped_target"),
        "warning_high",
        "alarm_high",
    ).write_csv(output_csv)
