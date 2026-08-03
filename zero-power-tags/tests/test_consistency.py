"""Consistency checks between the PowerTag annotation model and modbus_bridges.json.

The PowerTag annotation model is the single source of truth at runtime
(parse_topic builds ModbusTopic from it). These tests ensure the JSON-driven
ingestion path (scripts/excel_to_json.py + patches.json) cannot drift out of
sync with the annotations without failing CI.
"""

import json
from pathlib import Path

from zero_modbus_bridge.io import extract_modbus_fields

from zero_power_tags.io import PowerTag, read_modbus_topics

EXPECTED = {
    name: field
    for name, field in extract_modbus_fields(PowerTag).items()
}
EXPECTED_COUNT = 2
EXPECTED_DATA_TYPE = "float32"
EXPECTED_SCALE_FACTOR = 1.0


def _field_entries():
    """Yield every (unit_id, field_dict) from the checked-in bridges JSON."""
    json_path = Path(__file__).parent.parent / "modbus_bridges.json"
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    for unit in raw:
        for topic in unit["topics"]:
            yield unit["unit_id"], topic


def test_all_json_field_names_match_annotation():
    json_names = {
        field["field_name"]
        for _, topic in _field_entries()
        for field in topic["modbus_fields"]
    }
    assert json_names == set(EXPECTED), (
        f"Field-name drift between modbus_bridges.json and PowerTag annotation: "
        f"in JSON but not annotation: {sorted(json_names - set(EXPECTED))}; "
        f"in annotation but not JSON: {sorted(set(EXPECTED) - json_names)}"
    )


def test_every_field_metadata_matches_annotation():
    for _, topic in _field_entries():
        start_register = topic["modbus_fields"][0]["modbus_register"]
        for field in topic["modbus_fields"]:
            name = field["field_name"]
            expected = EXPECTED[name]
            offset = field["modbus_register"] - start_register
            assert (
                offset == expected.offset
            ), f"{name}: JSON offset {offset} != annotation offset {expected.offset}"
            assert (
                field["register_count"] == EXPECTED_COUNT
            ), f"{name}: register_count != {EXPECTED_COUNT}"
            assert (
                field["data_type"] == EXPECTED_DATA_TYPE
            ), f"{name}: data_type != {EXPECTED_DATA_TYPE}"
            assert (
                field.get("scale_factor", EXPECTED_SCALE_FACTOR) == EXPECTED_SCALE_FACTOR
            ), f"{name}: scale_factor != {EXPECTED_SCALE_FACTOR}"


def test_all_topics_parse():
    """The full checked-in bridges file must load through the runtime path."""
    topics = read_modbus_topics()
    assert len(topics) > 0
    assert all(t.converter is not None for t in topics)
