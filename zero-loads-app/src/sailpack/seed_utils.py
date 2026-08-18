import re
from pathlib import Path
from typing import Any

import polars as pl

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

SAIL_ABBREVIATION_ALIASES = {"MH0": "C0"}

MAPPING_FILE_NAME = "sailpack_mapping.csv"

NEWTON_PER_TONNE_FORCE = 9806.65


def escape_dollar_quoted_json(value: str) -> str:
    return value.replace("$$", "$ $")


def extract_sail_abbreviations(calculation_id: str) -> list[str]:
    raw_tokens = re.split(r"[^A-Za-z0-9]+", calculation_id.upper())
    filtered = [
        SAIL_ABBREVIATION_ALIASES.get(token, token)
        for token in raw_tokens
        if token in KNOWN_SAIL_ABBREVIATIONS or token in SAIL_ABBREVIATION_ALIASES
    ]

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(filtered))


def extract_load_cases(parsed: pl.DataFrame) -> pl.DataFrame:
    heel_lookup = (
        parsed.filter(pl.col("table_description") == "NOTES")
        .select(["Calculation ID", "Roll/Heel"])
        .with_columns(
            pl.col("Roll/Heel").str.strip_chars("° ").cast(pl.Float64).alias("heel")
        )
        .select(["Calculation ID", "heel"])
        .unique(subset=["Calculation ID"], keep="first")
    )

    return (
        (
            parsed.filter(pl.col("table_description") == "NAV. PARAMS")
            .select(
                [
                    "Calculation ID",
                    "TWS (Knts)",
                    "TWA (°)",
                    "AWS (Knts)",
                    "AWA (°)",
                    "BS (Knts)",
                ]
            )
            .rename(
                {
                    "TWS (Knts)": "tws",
                    "TWA (°)": "twa",
                    "AWS (Knts)": "aws",
                    "AWA (°)": "awa",
                    "BS (Knts)": "bsp",
                    "Calculation ID": "calculation_id",
                }
            )
            .join(
                heel_lookup,
                left_on="calculation_id",
                right_on="Calculation ID",
                how="left",
            )
            .select(["calculation_id", "tws", "twa", "aws", "awa", "bsp", "heel"])
        )
        .cast(
            {
                "tws": pl.Float64,
                "twa": pl.Float64,
                "aws": pl.Float64,
                "awa": pl.Float64,
                "calculation_id": pl.String,
                "heel": pl.Float64,
                "bsp": pl.Float64,
            }
        )
        .with_columns(pl.col("awa").abs())
        .unique(keep="first")
    )


def build_load_case_records(sailpack_data: pl.DataFrame) -> list[dict[str, Any]]:
    # Sail-set IDs are resolved during SQL execution against loads.sail_sets_combined.
    # We carry abbreviations here because we can extract them from sailpack without DB access.
    load_cases = extract_load_cases(sailpack_data)

    return [
        {
            "id": calc_id,
            "name": calc_id,
            "tws": tws,
            "twa": twa,
            "aws": aws,
            "awa": awa,
            "bsp": bsp,
            "heel": heel,
            "sail_abbreviations": sorted(abbreviations),
        }
        for calc_id, tws, twa, aws, awa, bsp, heel in load_cases.iter_rows()
        if (abbreviations := extract_sail_abbreviations(calc_id))
    ]


def extract_reference_values(
    sailpack_data: pl.DataFrame, reference_values_mapping: pl.DataFrame
) -> pl.DataFrame:
    cable_data = (
        sailpack_data.unpivot(
            ["Load (N) - After FSIC", "Trimming value (N or m) - FSIC trimmings"],
            index=["Calculation ID", "Cable name", "Trimming mode - FSIC trimmings"],
            variable_name="Column label",
        )
        .with_columns(
            pl.col("Column label")
            .str.strip_suffix(" - After FSIC")
            .str.strip_suffix(" - FSIC trimmings")
        )
        .filter(
            ~(
                (pl.col("Trimming mode - FSIC trimmings") == "Target load")
                & (pl.col("Column label") == "Trimming value (N or m)")
            )
        )
        .drop("Trimming mode - FSIC trimmings")
        .cast({"value": pl.Float64}, strict=False)
        .drop_nulls(subset=["value", "Cable name"])
    )

    reference_values_raw = (
        cable_data.join(
            reference_values_mapping,
            left_on=["Cable name", "Column label"],
            right_on=["Sailpack row label", "Sailpack column label"],
        )
        .select(
            [
                "Calculation ID",
                "Variable key",
                "Cable name",
                "value",
                "Column label",
            ]
        )
        .with_columns(
            pl.col("Column label")
            .replace({"Load (N)": "load", "Trimming value (N or m)": "position"})
            .cast(pl.Categorical)
            .alias("type")
        )
        .drop("Column label")
        .filter(
            pl.col("type") == "load"
        )  # TODO: remove later, but drop target positions for now as they require remapping to be useful as reference values
    )

    reference_values = reference_values_raw.with_columns(
        pl.when(pl.col("type") == "load")
        .then(pl.col("value") / NEWTON_PER_TONNE_FORCE)
        .otherwise(pl.col("value"))
        .alias("value")
    )

    reference_values_extended = (
        reference_values.pivot(
            index="Calculation ID",
            on="Variable key",
            values="value",
        )
        .with_columns(
            (pl.col("blade-adjuster-load") + pl.col("blade-cunningham-load")).alias(
                "main-headstay-combined-load"
            ),
            (pl.col("main-runner-load") + pl.col("main-checkstay-load")).alias(
                "main-runner-combined-load"
            ),
            (pl.col("mizzen-runner-load") + pl.col("mizzen-checkstay-load")).alias(
                "mizzen-runner-combined-load"
            ),
        )
        .unpivot(index="Calculation ID")
    )  # TODO: check correctness combined runner loads

    return reference_values_extended


def read_reference_values_mapping(mapping_path: Path) -> pl.DataFrame:
    if not mapping_path.exists():
        raise FileNotFoundError(f"Mapping file not found: {mapping_path}")

    return pl.read_csv(mapping_path)


def resolve_sail_set_id_sql(payload_alias: str = "payload") -> str:
    template = """(
            SELECT ssc.id
            FROM loads.sail_sets_combined AS ssc
            WHERE COALESCE(ssc.sails, '{}'::TEXT[]) = COALESCE(
                (
                    SELECT ARRAY_AGG(s.id ORDER BY s.id)
                    FROM loads.sails AS s
                    WHERE s.abbreviation = ANY(__PAYLOAD__.sail_abbreviations)
                ),
                '{}'::TEXT[]
            )
            LIMIT 1
        )"""
    return template.replace("__PAYLOAD__", payload_alias)
