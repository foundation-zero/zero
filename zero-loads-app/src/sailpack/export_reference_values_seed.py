import json
from typing import Any

import polars as pl

from sailpack.max_loads import THRESHOLD_COLUMNS, thresholded_variables
from sailpack.seed_utils import escape_dollar_quoted_json, resolve_sail_set_id_sql


def build_reference_records(reference_values: pl.DataFrame) -> list[dict[str, Any]]:
    return [
        {
            "load_case_id": row["Calculation ID"],
            "variable_id": row["variable"],
            "tack": row["tack"],
            "target": row["value"],
        }
        for row in reference_values.iter_rows(named=True)
    ]


def build_threshold_records(max_loads: pl.DataFrame) -> list[dict[str, Any]]:
    return [
        {
            "variable_id": row["variable"],
            **{column: row[column] for column in THRESHOLD_COLUMNS},
        }
        for row in thresholded_variables(max_loads).iter_rows(named=True)
    ]


def render_sql(
    load_case_records: list[dict[str, Any]],
    reference_records: list[dict[str, Any]],
    threshold_records: list[dict[str, Any]],
) -> str:
    # Sort for byte-deterministic output; the seed check compares exports byte-for-byte.
    sorted_load_case_records = sorted(
        load_case_records, key=lambda record: record["id"]
    )
    sorted_reference_records = sorted(
        reference_records,
        key=lambda record: (
            record["load_case_id"],
            record["tack"],
            record["variable_id"],
        ),
    )

    sorted_threshold_records = sorted(
        threshold_records, key=lambda record: record["variable_id"]
    )

    load_cases_json = escape_dollar_quoted_json(
        json.dumps(sorted_load_case_records, indent=2)
    )
    reference_json = escape_dollar_quoted_json(
        json.dumps(sorted_reference_records, indent=2)
    )
    thresholds_json = escape_dollar_quoted_json(
        json.dumps(sorted_threshold_records, indent=2)
    )

    return f"""DELETE FROM loads.thresholds;
DELETE FROM loads.reference_values;
DELETE FROM loads.load_case_mappings;
DELETE FROM loads.load_cases;

WITH load_case_payload AS (
    SELECT *
    FROM jsonb_to_recordset($${load_cases_json}$$::jsonb) AS t(
        id TEXT,
        name TEXT,
        tws NUMERIC,
        twa NUMERIC,
        aws NUMERIC,
        awa NUMERIC,
        bsp NUMERIC,
        heel NUMERIC,
        sail_abbreviations TEXT[]
    )
),
resolved_load_cases AS (
    SELECT
        payload.id,
        payload.name,
        payload.tws,
        payload.twa,
        payload.aws,
        payload.awa,
        payload.bsp,
        payload.heel,
        {resolve_sail_set_id_sql("payload")} AS sail_set_id
    FROM load_case_payload AS payload
),
upsert_load_cases AS (
    INSERT INTO loads.load_cases (id, name, tws, twa, aws, awa, bsp, heel, sail_set_id)
    SELECT
        id,
        name,
        tws,
        twa,
        aws,
        awa,
        bsp,
        heel,
        sail_set_id
    FROM resolved_load_cases
    ON CONFLICT (id) DO UPDATE
    SET
        name = EXCLUDED.name,
        tws = EXCLUDED.tws,
        twa = EXCLUDED.twa,
        aws = EXCLUDED.aws,
        awa = EXCLUDED.awa,
        bsp = EXCLUDED.bsp,
        heel = EXCLUDED.heel,
        sail_set_id = EXCLUDED.sail_set_id
    RETURNING id
),
reference_payload AS (
    SELECT *
    FROM jsonb_to_recordset($${reference_json}$$::jsonb) AS t(
        load_case_id TEXT,
        variable_id TEXT,
        tack TEXT,
        target NUMERIC
    )
)
INSERT INTO loads.reference_values (load_case_id, variable_id, tack, target)
SELECT
    payload.load_case_id,
    payload.variable_id,
    payload.tack,
    payload.target
FROM reference_payload AS payload
JOIN upsert_load_cases AS load_case
    ON load_case.id = payload.load_case_id
ON CONFLICT (load_case_id, tack, variable_id) DO UPDATE
SET target = EXCLUDED.target;

INSERT INTO loads.thresholds (variable_id, alarm_low, warning_low, warning_high, alarm_high)
SELECT variable_id, alarm_low, warning_low, warning_high, alarm_high
FROM jsonb_to_recordset($${thresholds_json}$$::jsonb) AS t(
    variable_id TEXT,
    alarm_low NUMERIC,
    warning_low NUMERIC,
    warning_high NUMERIC,
    alarm_high NUMERIC
);
"""
