import random
from unittest.mock import MagicMock

import pytest

from zero_data.data_gen import SailSystemGenerator
from zero_data.io_list.types import IOValue


@pytest.fixture
def generator():
    interval = MagicMock()
    mqtt_config = MagicMock()
    topics = MagicMock()
    random.seed(1)
    return SailSystemGenerator(interval, mqtt_config, topics)


@pytest.mark.parametrize(
    "data_type,check",
    [
        ("BOOLEAN", lambda v: isinstance(v, bool)),
        ("INTEGER", lambda v: isinstance(v, int)),
        ("REAL", lambda v: isinstance(v, float)),
        ("STRUCT<>", lambda v: isinstance(v, dict) and len(v) == 0),
    ],
)
def test_generate_random_value_simple(generator, data_type, check):
    field = IOValue(name="irrelevant", data_type=data_type)
    value = generator.generate_random_value(field)
    print(value)
    assert check(value)


def test_generate_random_value_unknown_type(generator):
    data_type = "not implemented"
    field = IOValue(name="irrelevant", data_type=data_type)
    with pytest.raises(KeyError) as e:
        generator.generate_random_value(field)

    assert e.match(f"Unknown type: {data_type}")


def test_generate_random_value_struct(generator):
    data_type = "STRUCT<a BOOLEAN, b INTEGER>"
    field = IOValue(name="irrelevant", data_type=data_type)
    value = generator.generate_random_value(field)

    assert isinstance(value, dict)
    assert list(value) == ["a", "b"]
    assert isinstance(value["a"], bool)
    assert isinstance(value["b"], int)


def test_generate_random_value_nested_struct(generator):
    data_type = "STRUCT<a BOOLEAN, b STRUCT<c INTEGER, d REAL>>"
    field = IOValue(name="irrelevant", data_type=data_type)
    value = generator.generate_random_value(field)
    print(value)
    assert isinstance(value, dict)
    assert list(value) == ["a", "b"]
    assert isinstance(value["a"], bool)
    assert isinstance(value["b"], dict)
    assert list(value["b"]) == ["c", "d"]
    assert isinstance(value["b"]["c"], int)
    assert isinstance(value["b"]["d"], float)
