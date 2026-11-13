import polars as pl
import pytest

from sailpack.seed_utils import (
    NEWTON_PER_TONNE_FORCE,
    add_derived_loads,
    assert_port_tack,
    extract_reference_values,
    extract_sail_abbreviations,
    mirror_side,
    read_reference_values_mapping,
)


def test_add_derived_loads():
    port_tack_loads = pl.DataFrame(
        {
            "Calculation ID": ["LC1"],
            "blade-adjuster-load": [30.0],
            "blade-cunningham-load": [20.0],
        }
    )

    derived = add_derived_loads(port_tack_loads).row(0, named=True)

    assert derived["main-headstay-combined-load"] == 50.0


def _sailpack_row(table_description: str, **cells: str) -> dict[str, str | None]:
    return {
        "table_description": table_description,
        "Calculation ID": "LC1",
        "Roll/Heel": None,
        "TWS (Knts)": None,
        "TWA (°)": None,
        "AWS (Knts)": None,
        "AWA (°)": None,
        "BS (Knts)": None,
        "Cable name": None,
        "Trimming mode - FSIC trimmings": None,
        "Load (N) - After FSIC": None,
        "Trimming value (N or m) - FSIC trimmings": None,
        **cells,
    }


def _cable_row(cable: str, tonnes: float) -> dict[str, str | None]:
    return _sailpack_row(
        "CABLE DATA",
        **{
            "Cable name": cable,
            "Trimming mode - FSIC trimmings": "Delta length",
            "Load (N) - After FSIC": str(tonnes * NEWTON_PER_TONNE_FORCE),
        },
    )


def test_extract_reference_values_multiplies_the_loads_by_their_purchase():
    sailpack_data = pl.DataFrame(
        [
            _sailpack_row("NOTES", **{"Roll/Heel": "20°"}),
            _sailpack_row(
                "NAV. PARAMS",
                **{
                    "TWS (Knts)": "20",
                    "TWA (°)": "-45",
                    "AWS (Knts)": "28",
                    "AWA (°)": "-30",
                    "BS (Knts)": "12",
                },
            ),
            _cable_row("CABLE__FS", 30.0),
            _cable_row("CABLE_BladeTACK", 20.0),
            _cable_row("RUNNER_TAIL", 10.0),
        ]
    )
    mapping = read_reference_values_mapping(
        "Technical name,Sailpack table name,Sailpack row label,Sailpack column label,"
        "Purchase (sailpack : function)\n"
        "blade-adjuster-load,CABLE DATA,CABLE__FS,Load (N),1\n"
        "blade-cunningham-load,CABLE DATA,CABLE_BladeTACK,Load (N),1\n"
        "main-runner-tail-ps-load,CABLE DATA,RUNNER_TAIL,Load (N),1\n"
        "main-runner-block-ps-load,CABLE DATA,RUNNER_TAIL,Load (N),2\n"
    )

    reference_values = {
        (row["variable"], row["tack"]): row["value"]
        for row in extract_reference_values(sailpack_data, mapping).iter_rows(
            named=True
        )
    }

    assert reference_values == pytest.approx(
        {
            ("blade-adjuster-load", "port"): 30.0,
            ("blade-cunningham-load", "port"): 20.0,
            ("main-runner-tail-ps-load", "port"): 10.0,
            ("main-runner-block-ps-load", "port"): 20.0,
            ("main-headstay-combined-load", "port"): 50.0,
            ("blade-adjuster-load", "starboard"): 30.0,
            ("blade-cunningham-load", "starboard"): 20.0,
            ("main-runner-tail-sb-load", "starboard"): 10.0,
            ("main-runner-block-sb-load", "starboard"): 20.0,
            ("main-headstay-combined-load", "starboard"): 50.0,
        }
    )


@pytest.mark.parametrize(
    ("calculation_id", "sails"),
    [
        ("LC4_ B_M1R_MZ2R_TWA45_TWS22_RM20_20240410", ["B", "M1R", "MZ2R"]),
        ("LC20_ MH0_FM_FMZ_ TWA70_TWS12_RM22_20240411", ["C0", "FM", "FMZ"]),
        ("LC66_TSOnly_TWS45_TWA70", ["TS"]),
        ("LC___FM_B_TWA45_TWS18_RM22_20241202 Main Tack Test", ["FM", "B"]),
        ("M1R M12R SS Upwind 20261009", ["M1R", "MZ1R", "SS"]),
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
