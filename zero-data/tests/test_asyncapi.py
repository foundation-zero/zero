from pathlib import Path

import pytest

from zero_data.asyncapi import JSON_TYPES, SCHEMA_REF_PREFIX, build_asyncapi, key
from zero_data.io_list import read_io_list
from zero_data.io_list.types import IOResult


@pytest.fixture(scope="module")
def io_result() -> IOResult:
    return read_io_list([Path("io_lists/ZERO mocked IO-List.xlsx")], "marpower")


@pytest.fixture(scope="module")
def document(io_result: IOResult) -> dict:
    return build_asyncapi(io_result)


def test_every_topic_has_one_channel_and_one_send_operation(
    io_result: IOResult, document: dict
):
    keys = {key(topic.topic) for topic in io_result.topics}

    assert set(document["channels"]) == keys
    assert set(document["operations"]) == keys
    for operation_key, operation in document["operations"].items():
        assert operation["action"] == "send"
        assert operation["channel"] == {"$ref": f"#/channels/{operation_key}"}


def test_address_keeps_the_devices_prefix_as_env_parameter(
    io_result: IOResult, document: dict
):
    for topic in io_result.topics:
        channel = document["channels"][key(topic.topic)]
        prefix, _, rest = channel["address"].partition("/")

        assert prefix == "{mqtt_devices_topic_prefix}"
        assert f"marpower/{rest}" == topic.topic
        assert (
            channel["parameters"]["mqtt_devices_topic_prefix"]["x-env"]
            == "MQTT_DEVICES_TOPIC_PREFIX"
        )


def test_every_field_is_a_stamped_value_of_its_data_type(
    io_result: IOResult, document: dict
):
    schemas = document["components"]["schemas"]
    for topic in io_result.topics:
        payload = document["channels"][key(topic.topic)]["messages"]["message"][
            "payload"
        ]

        assert set(payload["properties"]) == {field.name for field in topic.fields}
        for field in topic.fields:
            ref = payload["properties"][field.name]["$ref"]
            stamped = schemas[ref.removeprefix(SCHEMA_REF_PREFIX)]
            assert set(stamped["properties"]) == {"Value", "TimeStamp"}
            assert stamped["properties"]["Value"]["type"] == JSON_TYPES[field.data_type]


def test_document_does_not_depend_on_io_list_order(io_result: IOResult):
    reversed_result = IOResult(io_result.io_list, list(reversed(io_result.topics)))

    assert build_asyncapi(reversed_result) == build_asyncapi(io_result)
