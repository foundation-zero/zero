from dataclasses import dataclass
from enum import StrEnum

import polars as pl

from cheat_sheet.ui_dashboards import OverviewGroup
from loads.registry.registry import VARIABLES
from sailpack.export_load_case_mapping_seed import AWA_RANGES, awa_range_id
from sailpack.max_loads import THRESHOLD_COLUMNS, read_max_loads
from sailpack.seed_utils import (
    extract_load_cases,
    extract_reference_values,
    extract_sail_abbreviations,
    read_reference_values_mapping,
)

UNIT_SYMBOLS = {"tonne": "t", "ratio": "%"}

CONDITION_COLUMNS = ["tws", "twa", "aws", "awa", "bsp", "heel"]


class ThresholdLevel(StrEnum):
    NORMAL = "normal"
    WARNING = "warning"
    ALARM = "alarm"


@dataclass(frozen=True)
class Column:
    group: str
    technical_name: str
    label: str
    unit: str
    alarm_low: float | None
    warning_low: float | None
    warning_high: float | None
    alarm_high: float | None

    @property
    def is_position(self) -> bool:
        return self.unit == UNIT_SYMBOLS["ratio"]

    def threshold_level(self, value: float | None) -> ThresholdLevel:
        def outside(low: float | None, high: float | None) -> bool:
            return value is not None and (
                (low is not None and value < low) or (high is not None and value > high)
            )

        if outside(self.alarm_low, self.alarm_high):
            return ThresholdLevel.ALARM
        if outside(self.warning_low, self.warning_high):
            return ThresholdLevel.WARNING
        return ThresholdLevel.NORMAL


@dataclass(frozen=True)
class CheatSheet:
    """The port tack SailPack targets with load cases as rows and overview variables as columns.

    `load_cases` holds a row per load case: the number, section, calculation ID, file name, sails
    and conditions, followed by a column per technical name in `columns`.
    """

    load_cases: pl.DataFrame
    columns: list[Column]


def overview_columns(
    overview_groups: tuple[OverviewGroup, ...],
) -> list[tuple[str, str]]:
    """Return the group and technical name of every overview variable, in the first group it shows in."""
    first_groups = {
        technical_name: group.name
        for group in reversed(overview_groups)
        for technical_name in group.technical_names
    }
    return [
        (first_groups[technical_name], technical_name)
        for technical_name in dict.fromkeys(
            technical_name
            for group in overview_groups
            for technical_name in group.technical_names
        )
    ]


def build_columns(
    max_loads: pl.DataFrame, overview_groups: tuple[OverviewGroup, ...]
) -> list[Column]:
    thresholds = {row["variable"]: row for row in max_loads.iter_rows(named=True)}
    return [
        Column(
            group=group,
            technical_name=technical_name,
            label=VARIABLES[technical_name].name,
            unit=UNIT_SYMBOLS[VARIABLES[technical_name].unit],
            **{
                column: thresholds.get(technical_name, {}).get(column)
                for column in THRESHOLD_COLUMNS
            },
        )
        for group, technical_name in overview_columns(overview_groups)
    ]


def build_load_cases(sailpack_data: pl.DataFrame) -> pl.DataFrame:
    """Number the load cases by section (upwind, reaching, downwind) and then by AWA."""
    file_names = sailpack_data.select(
        pl.col("Calculation ID").alias("calculation_id"),
        (pl.col("source_file") + ".htm").alias("file_name"),
    ).unique()
    section_order = {section: order for order, section in enumerate(AWA_RANGES)}

    return (
        extract_load_cases(sailpack_data)
        .join(file_names, on="calculation_id")
        .with_columns(
            pl.col("awa")
            .map_elements(awa_range_id, return_dtype=pl.String)
            .alias("section"),
            pl.col("calculation_id")
            .map_elements(
                lambda calculation_id: " ".join(
                    extract_sail_abbreviations(calculation_id)
                ),
                return_dtype=pl.String,
            )
            .alias("sails"),
            pl.col("twa").abs(),
        )
        .sort(
            pl.col("section").replace_strict(section_order),
            "awa",
            "calculation_id",
        )
        .with_row_index("number", offset=1)
        .select(
            "number",
            "section",
            "calculation_id",
            "file_name",
            "sails",
            *CONDITION_COLUMNS,
        )
    )


def build_cheat_sheet(
    sailpack_data: pl.DataFrame,
    mapping_csv: str,
    max_loads_csv: str,
    overview_groups: tuple[OverviewGroup, ...],
) -> CheatSheet:
    columns = build_columns(read_max_loads(max_loads_csv), overview_groups)
    technical_names = [column.technical_name for column in columns]

    port_tack_targets = (
        extract_reference_values(
            sailpack_data, read_reference_values_mapping(mapping_csv)
        )
        .filter(pl.col("tack") == "port", pl.col("variable").is_in(technical_names))
        .pivot(index="Calculation ID", on="variable", values="value")
        .rename({"Calculation ID": "calculation_id"})
    )
    missing_columns = [
        pl.lit(None, dtype=pl.Float64).alias(technical_name)
        for technical_name in technical_names
        if technical_name not in port_tack_targets.columns
    ]

    load_cases = build_load_cases(sailpack_data)
    load_cases_with_targets = (
        load_cases.join(port_tack_targets, on="calculation_id", how="left")
        .with_columns(missing_columns)
        .select(*load_cases.columns, *technical_names)
    )
    return CheatSheet(load_cases=load_cases_with_targets, columns=columns)
