import math
from pathlib import Path

import polars as pl
import pytest

import sailpack
from sailpack.parse import parse_directory
from sailpack.seed_utils import (
    MAPPING_FILE_NAME,
    add_derived_loads,
    assert_port_tack,
    extract_reference_values,
    extract_sail_abbreviations,
    mirror_side,
    read_reference_values_mapping,
)

SAILPACK_DIRECTORY = Path(sailpack.__file__).parent

# Runner stay = tail factor × runner tail − checkstay × cos(checkstay angle), from the Vitters PLC
# formulas. The tolerance covers the SailPack geometry the PLC formulas simplify.
RUNNER_STAY_FORMULAS = {
    "main": (2, 10, 0.25),
    "mizzen": (2 * math.cos(math.radians(17)), 8, 0.4),
}


def test_add_derived_loads():
    port_tack_loads = pl.DataFrame(
        {
            "Calculation ID": ["LC1"],
            "blade-adjuster-load": [30.0],
            "blade-cunningham-load": [20.0],
            "main-runner-tail-ps-load": [13.0],
            "mizzen-runner-tail-ps-load": [5.0],
        }
    )

    derived = add_derived_loads(port_tack_loads).row(0, named=True)

    assert derived["main-headstay-combined-load"] == 50.0
    assert derived["main-runner-block-ps-load"] == 26.0
    assert derived["mizzen-runner-block-ps-load"] == pytest.approx(9.563, abs=1e-3)


@pytest.mark.parametrize(
    ("calculation_id", "sails"),
    [
        ("LC4_ B_M1R_MZ2R_TWA45_TWS22_RM20_20240410", ["B", "M1R", "MZ2R"]),
        ("LC20_ MH0_FM_FMZ_ TWA70_TWS12_RM22_20240411", ["C0", "FM", "FMZ"]),
        ("LC66_TSOnly_TWS45_TWA70", ["TS"]),
        ("LC___FM_B_TWA45_TWS18_RM22_20241202 Main Tack Test", ["FM", "B"]),
    ],
)
def test_extract_sail_abbreviations(calculation_id: str, sails: list[str]):
    assert extract_sail_abbreviations(calculation_id) == sails


@pytest.mark.parametrize(
    ("technical_name", "mirrored"),
    [
        ("main-runner-stay-ps-load", "main-runner-stay-sb-load"),
        ("blade-sheet-sb-load", "blade-sheet-ps-load"),
        ("fiber-optic-main-v1-ps", "fiber-optic-main-v1-sb"),
        ("blade-tweaker-sb-relative-position", "blade-tweaker-ps-relative-position"),
        (
            "fiber-optic-main-rigging-load-d2-port",
            "fiber-optic-main-rigging-load-d2-stbd",
        ),
        (
            "fiber-optic-mizzen-rigging-sum-load-v3-stbd",
            "fiber-optic-mizzen-rigging-sum-load-v3-port",
        ),
        ("main-headstay-combined-load", "main-headstay-combined-load"),
    ],
)
def test_mirror_side_swaps_sides(technical_name: str, mirrored: str):
    assert mirror_side(technical_name) == mirrored


def test_assert_port_tack_rejects_starboard_load_cases():
    load_cases = pl.DataFrame(
        {"calculation_id": ["port-case", "starboard-case"], "twa": [-45.0, 45.0]}
    )

    with pytest.raises(ValueError, match="starboard-case"):
        assert_port_tack(load_cases)


@pytest.fixture(scope="module")
def sailpack_reference_values() -> pl.DataFrame:
    return extract_reference_values(
        parse_directory(SAILPACK_DIRECTORY / "load_cases"),
        read_reference_values_mapping(SAILPACK_DIRECTORY / MAPPING_FILE_NAME),
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
