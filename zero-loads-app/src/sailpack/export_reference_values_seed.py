import json
import re
from pathlib import Path
from typing import Any

import polars as pl

from sailpack.parse import parse_directory
from sailpack.seed_utils import escape_dollar_quoted_json

KNOWN_SAIL_ABBREVIATIONS = {
    "FM",
    "M1R",
    "M2R",
    "M3R",
    "TS",
    "FMZ",
    "MZ1R",
    "MZ2R",
    "UM",
    "B",
    "C0",
    "A3",
    "A2",
    "SJ",
    "SS",
    "MZJ",
    "MZSS",
}

MAPPING_FILE_NAME = "Sailpack mapping - Mapping.csv"
NEWTON_PER_TONNE_FORCE = 9806.65


def parse_numeric(value: str | float | int | None) -> float | None:
    if value is None:
        return None

    if isinstance(value, int | float):
        return float(value)

    stripped = str(value).strip()
    if not stripped:
        return None

    lowered = stripped.lower()
    if lowered in {"null", "none", "nan", "-"}:
        return None

    try:
        return float(stripped)
    except ValueError:
        return None


def extract_sail_abbreviations(calculation_id: str) -> list[str]:
    raw_tokens = re.split(r"[^A-Za-z0-9]+", calculation_id.upper())
    filtered = [token for token in raw_tokens if token in KNOWN_SAIL_ABBREVIATIONS]

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(filtered))


def should_convert_newton_to_tonne(variable_key: str) -> bool:
    key = variable_key.lower()

    # Sailpack exports fiber optic tensions as loads but not all keys end with "-load".
    return "load" in key or key.startswith("fiber-optic-")


def newton_to_tonne(value: float) -> float:
    return value / NEWTON_PER_TONNE_FORCE


def _build_conditions(parsed: pl.DataFrame) -> pl.DataFrame:
    return (
        parsed.filter(pl.col("table_description") == "NAV. PARAMS")
        .select(["TWS (Knts)", "TWA (°)", "Calculation ID"])
        .cast(
            {
                "TWS (Knts)": pl.Float64,
                "TWA (°)": pl.Float64,
                "Calculation ID": pl.String,
            }
        )
        .rename(
            {
                "TWS (Knts)": "tws",
                "TWA (°)": "twa",
                "Calculation ID": "calculation_id",
            }
        )
    )


def _build_cable_data(parsed: pl.DataFrame, mapping: pl.DataFrame) -> pl.DataFrame:
    columns = [
        str(col)
        for col in mapping["Sailpack column label"].unique().drop_nulls().to_list()
    ]
    replacements = {
        "Load (N)": "Load (N) - After FSIC",
        "Trimming value (N or m)": "Trimming value (N or m) - FSIC trimmings",
    }
    replaced_cols: list[str] = [replacements.get(col, col) for col in columns]

    longed = parsed.unpivot(
        replaced_cols,
        index=["Calculation ID", "Cable name"],
        variable_name="result column label",
    )
    conditions = _build_conditions(parsed)

    return (
        mapping.filter(pl.col("Sailpack table name") == pl.lit("CABLE DATA"))
        .join_where(
            longed,
            [
                pl.col("Sailpack row label") == pl.col("Cable name"),
                pl.col("result column label").str.starts_with(
                    pl.col("Sailpack column label")
                ),
            ],
        )
        .join(conditions, left_on="Calculation ID", right_on="calculation_id")
        .select(
            [
                "Technical name (Loads app)",
                "value",
                "Calculation ID",
                "tws",
                "twa",
            ]
        )
    )


def _load_sailpack_input(input_source: Path) -> tuple[pl.DataFrame, pl.DataFrame]:
    if input_source.is_file():
        raise ValueError(
            "Expected a sailpack directory containing .htm files and mapping CSV, "
            f"got file: {input_source}"
        )

    if not input_source.exists():
        raise FileNotFoundError(f"Input directory not found: {input_source}")

    mapping_path = input_source / MAPPING_FILE_NAME
    if not mapping_path.exists():
        raise FileNotFoundError(f"Mapping file not found: {mapping_path}")

    parsed = parse_directory(str(input_source))
    mapping = pl.read_csv(mapping_path)
    conditions = _build_conditions(parsed)
    cable_data = _build_cable_data(parsed, mapping)
    return conditions, cable_data


def build_records(
    input_source: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    load_case_records: list[dict[str, Any]] = []
    reference_records: list[dict[str, Any]] = []

    conditions, cable_data = _load_sailpack_input(input_source)

    seen_load_cases: set[str] = set()
    for row in conditions.iter_rows(named=True):
        calculation_id = str(row["calculation_id"]).strip()
        if not calculation_id or calculation_id in seen_load_cases:
            continue

        aws = parse_numeric(row.get("tws"))
        awa_raw = parse_numeric(row.get("twa"))
        awa = abs(awa_raw) if awa_raw is not None else None

        if aws is None or awa is None:
            continue

        sail_abbreviations = extract_sail_abbreviations(calculation_id)

        load_case_records.append(
            {
                "id": calculation_id,
                "name": calculation_id,
                "awa": awa,
                "aws": aws,
                "sail_abbreviations": sail_abbreviations,
            }
        )
        seen_load_cases.add(calculation_id)

    for row in cable_data.iter_rows(named=True):
        calculation_id = str(row["Calculation ID"]).strip()

        variable_key_raw = row.get("Technical name (Loads app)")
        if variable_key_raw is None:
            continue

        variable_key = str(variable_key_raw).strip()

        if not calculation_id or not variable_key:
            continue

        target = parse_numeric(row.get("value"))
        if target is None:
            continue

        if should_convert_newton_to_tonne(variable_key):
            target = newton_to_tonne(target)

        reference_records.append(
            {
                "load_case_id": calculation_id,
                "variable_key": variable_key,
                "target": target,
                "alarm_low": None,
                "warning_low": None,
                "warning_high": None,
                "alarm_high": None,
            }
        )

    # Keep the first value per (load_case_id, variable_key) to satisfy the unique key.
    deduped_reference_records: dict[tuple[str, str], dict[str, Any]] = {}
    for record in reference_records:
        key = (record["load_case_id"], record["variable_key"])
        deduped_reference_records.setdefault(key, record)

    return load_case_records, list(deduped_reference_records.values())


def render_sql(
    load_case_records: list[dict[str, Any]], reference_records: list[dict[str, Any]]
) -> str:
    load_cases_json = escape_dollar_quoted_json(json.dumps(load_case_records, indent=2))
    reference_json = escape_dollar_quoted_json(json.dumps(reference_records, indent=2))

    return f"""-- Generated by src/sailpack/export_seed.py
-- Uses jsonb_to_recordset and resolves sail_set_id from sail abbreviations.

BEGIN;

WITH load_case_payload AS (
    SELECT *
    FROM jsonb_to_recordset($${load_cases_json}$$::jsonb) AS t(
        id TEXT,
        name TEXT,
        awa NUMERIC,
        aws NUMERIC,
        sail_abbreviations TEXT[]
    )
),
resolved_load_cases AS (
    SELECT
        payload.id,
        payload.name,
        payload.awa,
        payload.aws,
        (
            SELECT ssc.id
            FROM loads.sail_sets_combined AS ssc
            WHERE COALESCE(ssc.sails, '{{}}'::TEXT[]) = COALESCE(
                (
                    SELECT ARRAY_AGG(s.id ORDER BY s.id)
                    FROM loads.sails AS s
                    WHERE s.abbreviation = ANY(payload.sail_abbreviations)
                ),
                '{{}}'::TEXT[]
            )
            LIMIT 1
        ) AS sail_set_id
    FROM load_case_payload AS payload
),
upsert_load_cases AS (
    INSERT INTO loads.load_cases (id, name, awa, aws, sail_set_id)
    SELECT
        id,
        name,
        awa,
        aws,
        sail_set_id
    FROM resolved_load_cases
    ON CONFLICT (id) DO UPDATE
    SET
        name = EXCLUDED.name,
        awa = EXCLUDED.awa,
        aws = EXCLUDED.aws,
        sail_set_id = EXCLUDED.sail_set_id
    RETURNING id
),
reference_payload AS (
    SELECT *
    FROM jsonb_to_recordset($${reference_json}$$::jsonb) AS t(
        load_case_id TEXT,
        variable_key TEXT,
        target NUMERIC,
        alarm_low NUMERIC,
        warning_low NUMERIC,
        warning_high NUMERIC,
        alarm_high NUMERIC
    )
)
INSERT INTO loads.reference_values (
    load_case_id,
    variable_key,
    alarm_low,
    warning_low,
    target,
    warning_high,
    alarm_high
)
SELECT
    payload.load_case_id,
    payload.variable_key,
    payload.alarm_low,
    payload.warning_low,
    payload.target,
    payload.warning_high,
    payload.alarm_high
FROM reference_payload AS payload
JOIN upsert_load_cases AS load_case
    ON load_case.id = payload.load_case_id
ON CONFLICT (load_case_id, variable_key) DO UPDATE
SET
    alarm_low = EXCLUDED.alarm_low,
    warning_low = EXCLUDED.warning_low,
    target = EXCLUDED.target,
    warning_high = EXCLUDED.warning_high,
    alarm_high = EXCLUDED.alarm_high;

COMMIT;
"""


def export_seed_sql(input_source: Path, output_sql: Path) -> tuple[int, int]:
    load_case_records, reference_records = build_records(input_source)
    sql = render_sql(load_case_records, reference_records)
    output_sql.write_text(sql, encoding="utf-8")

    return len(load_case_records), len(reference_records)
