import math
from pathlib import Path

import polars as pl
import pytest

import sailpack
from loads.registry.sheets import LoadsSheet, consistency_problems
from sailpack.parse import parse_directory
from sailpack.seed_utils import extract_reference_values, read_reference_values_mapping

SAILPACK_DIRECTORY = Path(sailpack.__file__).parent

# Runner stay = runner block − checkstay × cos(checkstay angle), from the Vitters PLC formulas.
# The tolerance covers the SailPack geometry the PLC formulas simplify.
RUNNER_STAY_FORMULAS = {
    "main": (10, 0.25),
    "mizzen": (8, 0.4),
}


@pytest.fixture(scope="module")
def loads_sheet() -> LoadsSheet:
    return LoadsSheet.download()


def test_loads_sheet_is_consistent_with_the_registry(loads_sheet: LoadsSheet):
    assert consistency_problems(loads_sheet) == []


@pytest.fixture(scope="module")
def sailpack_reference_values(loads_sheet: LoadsSheet) -> pl.DataFrame:
    return extract_reference_values(
        parse_directory(SAILPACK_DIRECTORY / "load_cases"),
        read_reference_values_mapping(loads_sheet.sailpack_mapping),
    ).pivot(on="variable", index=["Calculation ID", "tack"], values="value")


@pytest.mark.parametrize("mast", RUNNER_STAY_FORMULAS)
@pytest.mark.parametrize(("tack", "side"), [("port", "ps"), ("starboard", "sb")])
def test_mapped_runner_stay_matches_the_plc_formula_from_the_mapped_block_and_checkstay(
    sailpack_reference_values: pl.DataFrame, mast: str, tack: str, side: str
):
    checkstay_angle_degrees, tolerance = RUNNER_STAY_FORMULAS[mast]
    deviations = (
        sailpack_reference_values.filter(pl.col("tack") == tack)
        .select(
            pl.col("Calculation ID"),
            (
                pl.col(f"{mast}-runner-stay-{side}-load")
                - pl.col(f"{mast}-runner-block-{side}-load")
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
