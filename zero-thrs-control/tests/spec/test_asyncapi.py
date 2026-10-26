from unittest.mock import Mock

import pytest
from asyncapi3.models import Channel, Operation, Server

# Adjust the import to match your actual module location
from thrs.input_output.base import ThrsValues
from thrs.runtime.descriptions.simulation import Mode
from thrs.spec.asyncapi import (
    CHANNEL_TTL,
    _build_asyncapi,
    _channel_key,
    _message_key,
    _operation_key,
)
from thrs.spec.recording_connector import TopicMapping

# ---------------------------------------------------------------------------
# Test Fixtures & Dummy Models
# ---------------------------------------------------------------------------


class NestedDetail(ThrsValues):
    code: int
    description: str


class SimplePayload(ThrsValues):
    status: str


class ComplexPayload(ThrsValues):
    reading: float
    detail: NestedDetail


@pytest.fixture
def sample_topics() -> list[TopicMapping]:
    return [
        TopicMapping(
            topic="actuators/valve",
            direction="send",
            payload_type=SimplePayload,
            component_type="valve",
        ),
        TopicMapping(
            topic="sensors/temperature",
            direction="receive",
            payload_type=ComplexPayload,
            component_type="temperature_sensor",
        ),
        TopicMapping(
            topic="sensors/pressure",
            direction="receive",
            payload_type=SimplePayload,  # Shared payload to test deduplication
            component_type="pressure_sensor",
        ),
    ]


@pytest.mark.parametrize(
    "topic,expected",
    [
        ("sensors/temperature", "sensors_temperature"),
        ("a/b/c/d", "a_b_c_d"),
        ("status", "status"),
        ("/leading/and/trailing/", "_leading_and_trailing_"),
    ],
)
def test_channel_key_generation(topic: str, expected: str):
    assert _channel_key(topic) == expected


@pytest.mark.parametrize(
    "topic,expected",
    [
        (
            Mock(topic="sensors/temperature"),
            "sensors_temperature",
        ),
        (Mock(topic="a/b/c/d"), "a_b_c_d"),
        (Mock(topic="status"), "status"),
        (
            Mock(topic="/leading/and/trailing/"),
            "_leading_and_trailing_",
        ),
    ],
)
def test_operation_key_generation(topic: Mock, expected: str):
    assert _operation_key(topic) == expected


def test_message_key_standard_class():
    assert _message_key(SimplePayload) == "test_asyncapiSimplePayload"


def test_message_key_removes_brackets():
    class MockGeneric[T](ThrsValues):
        pass

    assert _message_key(MockGeneric[int]) == "test_asyncapiMockGenericint"


def test_build_asyncapi_top_level_metadata():
    doc = _build_asyncapi("Custom Title", "2.0.0", Mode("thrs", {}, None), [])

    assert doc.asyncapi == "3.0.0"
    assert doc.info.title == "Custom Title"
    assert doc.info.version == "2.0.0"
    assert doc.default_content_type == "application/json"
    assert doc.servers
    assert "broker" in doc.servers.root
    assert isinstance(doc.servers.root["broker"], Server)
    assert doc.servers.root["broker"].protocol == "mqtt"
    assert doc.servers.root["broker"].protocol_version == "5.0"
    assert doc.servers.root["broker"].host == "localhost"


def test_build_asyncapi_channel_and_operation_mapping(
    sample_topics: list[TopicMapping],
):
    doc = _build_asyncapi(
        "THRS Control", "1.0.0", Mode("thrs", {}, None), sample_topics
    )

    for topic_data in sample_topics:
        channel_key = _channel_key(topic_data.topic)
        operation_key = _operation_key(topic_data)

        # Check Channel
        assert doc.channels
        assert channel_key in doc.channels.root
        channel = doc.channels.root[channel_key]
        assert isinstance(channel, Channel)
        assert channel.address == topic_data.topic

        ttl = getattr(channel, "x-ttl", None) or getattr(
            channel, "model_extra", {}
        ).get("x-ttl")
        component_type = getattr(channel, "x-zero-component-type", None) or getattr(
            channel, "model_extra", {}
        ).get("x-zero-component-type")
        assert ttl == CHANNEL_TTL
        assert component_type == topic_data.component_type

        # Check Operation
        assert doc.operations
        assert operation_key in doc.operations.root
        operation = doc.operations.root[operation_key]
        assert isinstance(operation, Operation)
        assert operation.action == topic_data.direction
        assert operation.channel.ref == f"#/channels/{channel_key}"


def test_build_asyncapi_message_deduplication(sample_topics: list[TopicMapping]):
    doc = _build_asyncapi("THRS Control", "1.0.0", Mode("", {}, None), sample_topics)  # type: ignore[arg-type]

    assert doc.components
    assert doc.components.messages
    assert doc.components.schemas

    # SimplePayload is shared between actuators/valve and sensors/pressure
    expected_message_keys = {
        "test_asyncapiSimplePayload",
        "test_asyncapiComplexPayload",
    }
    assert set(doc.components.messages.root.keys()) == expected_message_keys

    # ComplexPayload has NestedDetail in defs
    assert "NestedDetail" in doc.components.schemas.root


def test_build_asyncapi_topics_are_sorted():
    topics = [
        TopicMapping("z/topic", SimplePayload, "receive", "valve"),
        TopicMapping("a/topic", SimplePayload, "receive", "valve"),
        TopicMapping("m/topic", SimplePayload, "receive", "valve"),
    ]
    doc = _build_asyncapi("THRS", "1.0", Mode("", {}, None), topics)  # type: ignore[arg-type]

    assert doc.channels
    channel_keys = list(doc.channels.root.keys())
    assert channel_keys == ["a_topic", "m_topic", "z_topic"]
