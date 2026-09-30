import polars as pl
import pytest

from sailpack.seed_utils import assert_port_tack, mirror_side


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
