import re
from pathlib import Path

import polars as pl
import pytest

from cheat_sheet.build import (
    OVERVIEW_GROUPS,
    UNIT_SYMBOLS,
    Column,
    OverviewGroup,
    ThresholdLevel,
    build_columns,
    build_load_cases,
    overview_columns,
)
from cheat_sheet.pdf import BOOKLET_LOAD_CASES, headsail_category, table_rows
from loads.registry.registry import VARIABLES
from sailpack.seed_utils import KNOWN_SAIL_ABBREVIATIONS

UI_DASHBOARDS = (
    Path(__file__).parents[3] / "zero-ui/src/modules/loads/lib/consts.dashboards.ts"
)


def _ui_overview_groups() -> tuple[OverviewGroup, ...]:
    dashboards = UI_DASHBOARDS.read_text()
    group_definitions = {
        constant: OverviewGroup(name, tuple(re.findall(r'"([a-z0-9-]+)"', variables)))
        for constant, name, variables in re.findall(
            r'export const (\w+_GROUP) = group\(\s*"([^"]+)",\s*PositionId\.\w+,(.*?)\);',
            dashboards,
            flags=re.DOTALL,
        )
    }
    overview = re.search(
        r"export const OVERVIEW = dashboard\((.*?)\);", dashboards, re.DOTALL
    )
    assert overview is not None
    return tuple(
        group_definitions[constant]
        for constant in re.findall(r"\w+_GROUP", overview.group(1))
    )


def _column(
    technical_name: str = "main-vang-load",
    group: str = "Main sail",
    unit: str = "t",
    alarm_low: float | None = None,
    warning_low: float | None = None,
    warning_high: float | None = None,
    alarm_high: float | None = None,
) -> Column:
    return Column(
        group=group,
        technical_name=technical_name,
        label=technical_name,
        unit=unit,
        alarm_low=alarm_low,
        warning_low=warning_low,
        warning_high=warning_high,
        alarm_high=alarm_high,
    )


def test_overview_groups_match_the_ui_overview_dashboard():
    assert OVERVIEW_GROUPS == _ui_overview_groups()


def test_overview_variables_are_in_the_registry_with_a_known_unit():
    assert all(
        technical_name in VARIABLES and VARIABLES[technical_name].unit in UNIT_SYMBOLS
        for _, technical_name in overview_columns()
    )


def test_overview_columns_keep_each_variable_once_in_its_first_group():
    columns = overview_columns()

    assert len(columns) == len({technical_name for _, technical_name in columns})
    assert ("Storm Jib", "primary-winch-ps-load") in columns
    assert ("Mizzen jib", "mizzen-headsail-tack-adjuster-load") in columns


def test_build_columns_label_with_the_ui_label_and_add_the_thresholds():
    max_loads = pl.DataFrame(
        {
            "variable": ["main-vang-load"],
            "alarm_low": [None],
            "warning_low": [None],
            "warning_high": [40.0],
            "alarm_high": [43.0],
        },
        schema_overrides={"alarm_low": pl.Float64, "warning_low": pl.Float64},
    )

    columns = {column.technical_name: column for column in build_columns(max_loads)}

    assert columns["main-vang-load"].label == VARIABLES["main-vang-load"].name
    assert columns["main-vang-load"].warning_high == 40.0
    assert columns["main-sheet-load"].alarm_high is None


@pytest.mark.parametrize(
    ("value", "level"),
    [
        (None, ThresholdLevel.NORMAL),
        (20.0, ThresholdLevel.NORMAL),
        (28.0, ThresholdLevel.NORMAL),
        (29.0, ThresholdLevel.WARNING),
        (32.0, ThresholdLevel.ALARM),
        (8.0, ThresholdLevel.WARNING),
        (7.0, ThresholdLevel.ALARM),
    ],
)
def test_threshold_level_flags_targets_outside_the_warnings_and_alarms(
    value: float | None, level: ThresholdLevel
):
    column = _column(alarm_low=7.5, warning_low=8.4, warning_high=28.0, alarm_high=31.3)

    assert column.threshold_level(value) == level


def test_build_load_cases_numbers_by_section_and_then_awa():
    def nav_params(calculation_id: str, awa: str) -> dict[str, str]:
        return {
            "table_description": "NAV. PARAMS",
            "Calculation ID": calculation_id,
            "source_file": calculation_id,
            "TWS (Knts)": "20",
            "TWA (°)": "-60",
            "AWS (Knts)": "30",
            "AWA (°)": awa,
            "BS (Knts)": "12",
        }

    def notes(calculation_id: str) -> dict[str, str]:
        return {
            "table_description": "NOTES",
            "Calculation ID": calculation_id,
            "source_file": calculation_id,
            "Roll/Heel": "20°",
        }

    calculation_awas = {"LC2_ SS_M1R": "-45", "LC1_ B_FM_FMZ": "-30", "LC3_ SJ": "-20"}
    sailpack_data = pl.DataFrame(
        [
            *(
                nav_params(calculation_id, awa)
                for calculation_id, awa in calculation_awas.items()
            ),
            *(notes(calculation_id) for calculation_id in calculation_awas),
        ]
    )

    load_cases = build_load_cases(sailpack_data)

    assert load_cases.select("number", "section", "calculation_id", "sails").rows() == [
        (1, "upwind", "LC3_ SJ", "SJ"),
        (2, "upwind", "LC1_ B_FM_FMZ", "B FM FMZ"),
        (3, "reaching", "LC2_ SS_M1R", "SS M1R"),
    ]
    assert load_cases["file_name"].to_list() == [
        "LC3_ SJ.htm",
        "LC1_ B_FM_FMZ.htm",
        "LC2_ SS_M1R.htm",
    ]
    assert load_cases["twa"].to_list() == [60.0, 60.0, 60.0]


def test_table_rows_pair_loads_with_their_relative_position():
    vang = _column("main-vang-load")
    vang_position = _column("main-vang-relative-position", unit="%")
    traveller_position = _column("main-traveller-relative-position", unit="%")
    sheet = _column("main-sheet-load")

    rows = table_rows([sheet, traveller_position, vang, vang_position])

    assert [(row.column, row.load, row.position) for row in rows] == [
        (sheet, sheet, None),
        (traveller_position, None, None),
        (vang, vang, vang_position),
    ]


@pytest.mark.parametrize(
    ("sails", "category"),
    [
        ("B FM FMZ MZJ", "Blade"),
        ("SS M1R MZ2R", "Staysail"),
        ("M3R SJ", "Storm jib"),
        ("C0 FM FMZ", "Code zero"),
        ("TS", "Trisail"),
        ("FM FMZ", "No headsail"),
    ],
)
def test_headsail_category(sails: str, category: str):
    assert headsail_category(sails) == category


def test_booklet_sail_sets_use_known_sail_abbreviations():
    assert all(sail_set <= KNOWN_SAIL_ABBREVIATIONS for sail_set in BOOKLET_LOAD_CASES)
