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


def apply_max_loads(
    reference_values: pl.DataFrame, max_loads: pl.DataFrame
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Add warning and alarm thresholds to every load case and tack.

    Targets above a threshold would violate the reference_values CHECK constraints, so they are
    dropped and returned separately as conflicts.
    """
    load_case_tacks = reference_values.select("Calculation ID", "tack").unique()
    threshold_only_variables = (
        max_loads.filter(
            pl.col("warning_high").is_not_null() | pl.col("alarm_high").is_not_null()
        )
        .join(reference_values.select("variable").unique(), on="variable", how="anti")
        .select("variable")
    )

    all_reference_values = pl.concat(
        [
            reference_values.select("Calculation ID", "variable", "value", "tack"),
            load_case_tacks.join(threshold_only_variables, how="cross").select(
                "Calculation ID",
                "variable",
                pl.lit(None, dtype=pl.Float64).alias("value"),
                "tack",
            ),
        ]
    ).join(max_loads, on="variable", how="left")

    exceeds_threshold = pl.col("value").is_not_null() & (
        (pl.col("value") > pl.col("warning_high")).fill_null(False)
        | (pl.col("value") > pl.col("alarm_high")).fill_null(False)
    )

    conflicts = all_reference_values.filter(exceeds_threshold).sort(
        "variable", "Calculation ID", "tack"
    )
    reference_values_with_thresholds = all_reference_values.with_columns(
        pl.when(exceeds_threshold).then(None).otherwise(pl.col("value")).alias("value")
    )

    return reference_values_with_thresholds, conflicts


def write_conflicts(conflicts: pl.DataFrame, output_csv: Path) -> None:
    conflicts.select(
        pl.col("variable").alias("technical_name"),
        pl.col("Calculation ID").alias("load_case_id"),
        "tack",
        pl.col("value").round(3).alias("dropped_target"),
        "warning_high",
        "alarm_high",
    ).write_csv(output_csv)
