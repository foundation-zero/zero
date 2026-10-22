import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from sailpack.seed_utils import escape_dollar_quoted_json, resolve_sail_set_id_sql

AWA_RANGES: dict[str, tuple[float, float]] = {
    "upwind": (0.0, 40.0),
    "reaching": (40.0, 80.0),
    "downwind": (80.0, 180.0),
}

AWS_RANGES: list[tuple[float, float | None]] = [
    (0.0, 10.0),
    (10.0, 15.0),
    (15.0, 20.0),
    (20.0, 25.0),
    (25.0, 30.0),
    (30.0, 40.0),
    (40.0, None),
]


def _aws_distance(aws: float, lower: float, upper: float | None) -> float:
    if aws < lower:
        return lower - aws
    if upper is not None and aws >= upper:
        return aws - upper
    return 0.0


def _awa_contains(awa: float, range_id: str) -> bool:
    lower, upper = AWA_RANGES[range_id]
    if range_id == "downwind":
        return lower <= awa <= upper
    return lower <= awa < upper


def awa_range_id(awa: float) -> str:
    return next(range_id for range_id in AWA_RANGES if _awa_contains(awa, range_id))


@dataclass(frozen=True)
class AmbiguousLoadCases:
    """Load cases in the same sail set, AWA range and AWS range; the first ID is mapped."""

    sail_abbreviations: tuple[str, ...]
    awa_range_id: str
    aws_range: tuple[float, float | None]
    load_case_ids: list[str]


def _aws_range_index(aws: float) -> int:
    return next(
        index
        for index, (lower, upper) in enumerate(AWS_RANGES)
        if lower <= aws and (upper is None or aws < upper)
    )


def find_ambiguous_load_cases(
    load_case_records: list[dict[str, Any]],
) -> list[AmbiguousLoadCases]:
    by_range: dict[tuple[tuple[str, ...], str, int], list[str]] = defaultdict(list)
    for lc in load_case_records:
        key = (
            tuple(sorted(lc["sail_abbreviations"])),
            awa_range_id(lc["awa"]),
            _aws_range_index(lc["aws"]),
        )
        by_range[key].append(lc["id"])

    return [
        AmbiguousLoadCases(
            sail_abbreviations=sail_abbreviations,
            awa_range_id=awa_range_id,
            aws_range=AWS_RANGES[aws_range_index],
            load_case_ids=sorted(load_case_ids),
        )
        for (
            sail_abbreviations,
            awa_range_id,
            aws_range_index,
        ), load_case_ids in sorted(by_range.items())
        if len(load_case_ids) > 1
    ]


def build_records(load_case_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_sails: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for lc in load_case_records:
        key = tuple(sorted(lc["sail_abbreviations"]))
        by_sails[key].append(lc)

    records = [
        {
            "load_case_id": best["id"],
            "awa_range_id": awa_range_id,
            "aws_range_id": aws_range_id
            + 1,  # AWS_RANGES is 0-indexed, but the DB is 1-indexed
            "sail_abbreviations": list(sail_abbreviations),
        }
        for sail_abbreviations, candidates in sorted(by_sails.items())
        for awa_range_id in AWA_RANGES
        if (
            awa_candidates := [
                lc for lc in candidates if _awa_contains(lc["awa"], awa_range_id)
            ]
        )
        for aws_range_id, (aws_lower, aws_upper) in enumerate(AWS_RANGES)
        if (
            best := min(
                awa_candidates,
                key=lambda lc, lower=aws_lower, upper=aws_upper: (
                    _aws_distance(lc["aws"], lower, upper),
                    lc["id"],
                ),
            )
        )
    ]

    return records


def render_sql(records: list[dict[str, Any]]) -> str:
    mapping_json = escape_dollar_quoted_json(json.dumps(records, indent=2))

    return f"""WITH mapping_payload AS (
    SELECT *
    FROM jsonb_to_recordset($${mapping_json}$$::jsonb) AS t(
        load_case_id TEXT,
        awa_range_id TEXT,
        aws_range_id INT,
        sail_abbreviations TEXT[]
    )
),
resolved_mappings AS (
    SELECT
        payload.load_case_id,
        payload.awa_range_id,
        payload.aws_range_id,
        {resolve_sail_set_id_sql("payload")} AS sail_set_id
    FROM mapping_payload AS payload
)
INSERT INTO loads.load_case_mappings (
    load_case_id,
    awa_range_id,
    aws_range_id,
    sail_set_id
)
SELECT
    load_case_id,
    awa_range_id,
    aws_range_id,
    sail_set_id
FROM resolved_mappings
WHERE sail_set_id IS NOT NULL
ON CONFLICT (awa_range_id, aws_range_id, sail_set_id) DO UPDATE
SET
    load_case_id = EXCLUDED.load_case_id;
"""
