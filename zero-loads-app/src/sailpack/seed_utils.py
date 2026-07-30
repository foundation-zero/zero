import re
from pathlib import Path

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

MAPPING_FILE_NAME = "Sailpack mapping - Mapping.csv"


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


def extract_reference_values(
    parsed: pl.DataFrame, mapping: pl.DataFrame
) -> pl.DataFrame:
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

    cases = extract_load_cases(parsed)

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
        .join(cases, left_on="Calculation ID", right_on="calculation_id")
    )


def read_reference_values_mapping(input_source: Path) -> pl.DataFrame:
    mapping_path = input_source / MAPPING_FILE_NAME
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
