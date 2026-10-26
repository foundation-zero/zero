from typing import Any

from sailpack.export_load_case_mapping_seed import (
    AmbiguousLoadCases,
    find_ambiguous_load_cases,
)


def _load_case(id: str, sails: list[str], awa: float, aws: float) -> dict[str, Any]:
    return {"id": id, "sail_abbreviations": sails, "awa": awa, "aws": aws}


def test_find_ambiguous_load_cases_groups_by_sail_set_awa_range_and_aws_range():
    load_cases = [
        _load_case("M3R SJ Upwind", ["M3R", "SJ"], awa=25.0, aws=43.8),
        _load_case("M3R SJ Rchng", ["SJ", "M3R"], awa=50.0, aws=42.9),
        _load_case("M3R SJ other AWS range", ["M3R", "SJ"], awa=25.0, aws=38.0),
        _load_case("M3R SJ reaching", ["M3R", "SJ"], awa=70.0, aws=43.0),
        _load_case("M2R SJ", ["M2R", "SJ"], awa=25.0, aws=43.0),
    ]

    assert find_ambiguous_load_cases(load_cases) == [
        AmbiguousLoadCases(
            sail_abbreviations=("M3R", "SJ"),
            awa_range_id="reaching",
            aws_range=(40.0, None),
            load_case_ids=["M3R SJ Rchng", "M3R SJ reaching"],
        )
    ]
