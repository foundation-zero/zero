import json
from pathlib import Path
from typing import get_args

import pytest

from thrs.runtime.descriptions.simulation import ModeName

SCHEMA_PATH = (
    Path(__file__).parents[2] / "charts" / "zero-thrs-control" / "values.schema.json"
)

# ModeName is a PEP 695 alias, so the Literal members live behind __value__.
MODE_NAMES = set(get_args(ModeName.__value__))


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def test_control_types_enum_matches_mode_names(schema: dict):
    enum = schema["properties"]["control"]["properties"]["types"]["items"]["enum"]

    assert set(enum) == MODE_NAMES


def test_simulation_type_enum_matches_mode_names(schema: dict):
    enum = schema["properties"]["simulation"]["properties"]["type"]["enum"]

    assert set(enum) == MODE_NAMES


def test_simulation_type_default_is_a_mode_name(schema: dict):
    default = schema["properties"]["simulation"]["properties"]["type"]["default"]

    assert default in MODE_NAMES
