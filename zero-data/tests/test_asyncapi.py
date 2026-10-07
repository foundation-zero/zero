from pathlib import Path

import pytest

from zero_data.asyncapi import (
    JSON_TYPES,
    SCHEMA_REF_PREFIX,
    build_asyncapi,
    key,
    served_fields,
)
from zero_data.io_list import read_io_list
from zero_data.io_list.managed_topics import ManagedTopic, extract_managed_topics
from zero_data.io_list.types import IOResult, IOTopic, IOValue


@pytest.fixture(scope="module")
def io_result() -> IOResult:
    return read_io_list([Path("io_lists/ZERO mocked IO-List.xlsx")], "marpower")


@pytest.fixture(scope="module")
def managed_topics(io_result: IOResult) -> list[ManagedTopic]:
    managed_topics, *_ = extract_managed_topics(io_result.topics)

    return managed_topics


@pytest.fixture(scope="module")
def document(io_result: IOResult) -> dict:
    return build_asyncapi(io_result)


def test_every_topic_has_one_channel_and_one_send_operation(
    managed_topics: list[ManagedTopic], document: dict
):
    keys = {key(topic) for topic in managed_topics}

    assert set(document["channels"]) == keys
    assert set(document["operations"]) == keys
    for operation_key, operation in document["operations"].items():
        assert operation["action"] == "receive"
        assert operation["channel"] == {"$ref": f"#/channels/{operation_key}"}


def test_every_field_is_a_stamped_value_of_its_data_type(
    managed_topics: list[ManagedTopic], document: dict
):
    schemas = document["components"]["schemas"]
    for topic in managed_topics:
        payload = document["channels"][key(topic)]["messages"]["message"]["payload"]

        assert set(payload["properties"]) == {
            field for field in served_fields(topic.topic)
        }
        for field in topic.topic.fields:
            ref = payload["properties"][field.name]["$ref"]
            stamped = schemas[ref.removeprefix(SCHEMA_REF_PREFIX)]
            assert set(stamped["properties"]) == {"Value", "TimeStamp"}
            assert stamped["properties"]["Value"]["type"] == JSON_TYPES[field.data_type]


def test_document_does_not_depend_on_io_list_order(io_result: IOResult):
    reversed_result = IOResult(io_result.io_list, list(reversed(io_result.topics)))

    assert build_asyncapi(reversed_result) == build_asyncapi(io_result)


def test_fields_whose_graphql_names_collide_are_both_left_out(caplog):
    topic = IOTopic(
        "marpower/280000-hydraulic-sail/hydraulics",
        [
            IOValue("Tank_Level_Sensor", "BOOLEAN"),
            IOValue("Tank_level_sensor", "INTEGER"),
            IOValue("Pressure", "REAL"),
            IOValue("Temperature", "REAL", yard_tag="50001038-41"),
            IOValue("Temperature", "REAL", yard_tag="50001038-42"),
        ],
    )

    assert [field for field in served_fields(topic)] == ["Pressure", "Temperature"]
    assert "Tank_Level_Sensor, Tank_level_sensor" in caplog.text
