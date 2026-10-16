import math
from pathlib import Path

import polars as pl
import pytest

import sailpack
from loads.registry.sheets import (
    IoListLabel,
    LoadsSheet,
    consistency_problems,
    io_list_labels,
)
from sailpack.parse import parse_directory
from sailpack.seed_utils import extract_reference_values, read_reference_values_mapping

SAILPACK_DIRECTORY = Path(sailpack.__file__).parent

# Runner stay = tail factor × runner tail − checkstay × cos(checkstay angle), from the Vitters PLC
# formulas. The tolerance covers the SailPack geometry the PLC formulas simplify.
RUNNER_STAY_FORMULAS = {
    "main": (2, 10, 0.25),
    "mizzen": (2 * math.cos(math.radians(17)), 8, 0.4),
}


@pytest.fixture(scope="module")
def loads_sheet() -> LoadsSheet:
    return LoadsSheet.download()


def test_loads_sheet_is_consistent_with_the_registry(loads_sheet: LoadsSheet):
    assert consistency_problems(loads_sheet) == []


def test_io_list_labels_join_on_topic_regardless_of_case(loads_sheet: LoadsSheet):
    labels = io_list_labels(loads_sheet.vitters_io_list)

    assert labels["blade-adjuster-load"] == IoListLabel(
        display_name="Blade RTA Load",
        abbreviated_display_name="B RTA",
        display_units="t",
    )
    assert labels["mast-lock-main-1"].display_name == "Main Reef 1 lock"


@pytest.fixture(scope="module")
def sailpack_reference_values(loads_sheet: LoadsSheet) -> pl.DataFrame:
    return extract_reference_values(
        parse_directory(SAILPACK_DIRECTORY / "load_cases"),
        read_reference_values_mapping(loads_sheet.sailpack_mapping),
    ).pivot(on="variable", index=["Calculation ID", "tack"], values="value")


@pytest.mark.parametrize("mast", RUNNER_STAY_FORMULAS)
@pytest.mark.parametrize(("tack", "side"), [("port", "ps"), ("starboard", "sb")])
def test_mapped_runner_stay_matches_the_plc_formula_from_the_mapped_tail_and_checkstay(
    sailpack_reference_values: pl.DataFrame, mast: str, tack: str, side: str
):
    tail_factor, checkstay_angle_degrees, tolerance = RUNNER_STAY_FORMULAS[mast]
    deviations = (
        sailpack_reference_values.filter(pl.col("tack") == tack)
        .select(
            pl.col("Calculation ID"),
            (
                pl.col(f"{mast}-runner-stay-{side}-load")
                - tail_factor * pl.col(f"{mast}-runner-tail-{side}-load")
                + pl.col(f"{mast}-checkstay-{side}-load")
                * math.cos(math.radians(checkstay_angle_degrees))
            )
            .abs()
            .alias("deviation"),
        )
        .drop_nulls()
    )

    assert (
        deviations.height
        == sailpack_reference_values.filter(pl.col("tack") == tack).height
    )
    assert deviations.filter(pl.col("deviation") > tolerance).to_dicts() == []
