from enum import Enum
from unittest.mock import Mock

import pytest
from asyncapi3.models import Channel, Operation, Server

# Adjust the import to match your actual module location
from thrs.input_output.base import ThrsValues, simulation_type_field
from thrs.orchestration.config import Config
from thrs.runtime.descriptions.simulation import MODES, Mode
from thrs.spec.asyncapi import (
    CHANNEL_TTL,
    _build_asyncapi,
    _channel_key,
    _message_key,
    _operation_key,
    generate_asyncapi,
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


def test_build_asyncapi_yard_tag_on_channel():
    topics = [
        TopicMapping("a/tagged", SimplePayload, "send", "pump", yard_tag="50001018"),
        TopicMapping("a/untagged", SimplePayload, "send", "pump"),
    ]
    doc = _build_asyncapi("THRS", "1.0", Mode("", {}, None), topics)  # type: ignore[arg-type]

    assert doc.channels
    channels = {
        key: channel.model_dump(by_alias=True, exclude_none=True)
        for key, channel in doc.channels.root.items()
    }
    assert channels["a_tagged"]["x-zero-yard-tag"] == "50001018"
    assert "x-zero-yard-tag" not in channels["a_untagged"]


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


class Level(Enum):
    LOW = 1
    HIGH = 3


class LevelPayload(ThrsValues):
    level: Level


def test_build_asyncapi_names_enum_values():
    topics = [TopicMapping("pump/level", LevelPayload, "send", "pump")]
    doc = _build_asyncapi("THRS", "1.0", Mode("", {}, None), topics)  # type: ignore[arg-type]

    assert doc.components
    assert doc.components.schemas
    level = doc.components.schemas.root["Level"].model_dump(
        by_alias=True, exclude_none=True
    )
    assert level["type"] == "integer"
    assert level["oneOf"] == [
        {"const": 1, "title": "LOW"},
        {"const": 3, "title": "HIGH"},
    ]
    assert "enum" not in level


class PvtPayload(ThrsValues):
    simulation_type = simulation_type_field("pvt")
    pvt_level: int


class DhwPayload(ThrsValues):
    simulation_type = simulation_type_field("dhw")
    dhw_level: int


def test_build_asyncapi_unions_the_payloads_of_one_topic():
    topics = [
        TopicMapping("sim/inputs", PvtPayload, "send", None),
        TopicMapping("sim/inputs", DhwPayload, "send", None),
        TopicMapping("sim/inputs/set", PvtPayload, "receive", None),
        TopicMapping("sim/inputs/set", DhwPayload, "receive", None),
    ]
    union_names = {"sim/inputs": "Inputs", "sim/inputs/set": "Inputs"}
    doc = _build_asyncapi("THRS", "1.0", Mode("", {}, None), topics, union_names)  # type: ignore[arg-type]

    assert doc.channels
    assert set(doc.channels.root) == {"sim_inputs", "sim_inputs_set"}
    assert doc.components
    assert doc.components.messages
    assert set(doc.components.messages.root) == {"Inputs"}
    message = doc.components.messages.root["Inputs"].model_dump(
        by_alias=True, exclude_none=True
    )
    assert message["payload"] == {"$ref": "#/components/schemas/Inputs"}
    assert doc.components.schemas
    union = doc.components.schemas.root["Inputs"].model_dump(
        by_alias=True, exclude_none=True
    )
    assert union == {
        "type": "object",
        "discriminator": "SimulationType",
        "required": ["SimulationType"],
        "properties": {"SimulationType": {"type": "string", "enum": ["pvt", "dhw"]}},
        "oneOf": [
            {"$ref": "#/components/schemas/PvtPayload"},
            {"$ref": "#/components/schemas/DhwPayload"},
        ],
    }


def test_build_asyncapi_needs_a_union_name_for_several_payloads():
    topics = [
        TopicMapping("sim/inputs", PvtPayload, "send", None),
        TopicMapping("sim/inputs", DhwPayload, "send", None),
    ]

    with pytest.raises(ValueError, match="sim/inputs carries 2 payload classes"):
        _build_asyncapi("THRS", "1.0", Mode("", {}, None), topics)  # type: ignore[arg-type]


def test_spec_unions_every_simulation_mode_on_the_simulator_topics():
    config = Config(
        mqtt_host="",
        mqtt_port=0,
        mqtt_devices_topic_prefix="marpower",
        mqtt_controller_topic_prefix="thrs/controller",
        mqtt_controller_topic_suffix="set",
        mqtt_simulator_topic_prefix="thrs/simulator",
        mqtt_simulator_topic_suffix="set",
        mqtt_control_topic_suffix="Command",
    )
    spec = generate_asyncapi(config).model_dump(by_alias=True, exclude_none=True)

    channels = spec["channels"]
    assert channels["thrs_simulator_simulation-inputs"]["messages"] == {
        "message": {"$ref": "#/components/messages/SimulationInputs"}
    }
    assert channels["thrs_simulator_simulation-inputs_set"]["messages"] == {
        "message": {"$ref": "#/components/messages/SimulationInputs"}
    }
    assert channels["thrs_simulator_simulation-outputs"]["messages"] == {
        "message": {"$ref": "#/components/messages/SimulationOutputs"}
    }
    schemas = spec["components"]["schemas"]
    names = [mode.name for mode in MODES if mode.simulation_description]
    for union in ("SimulationInputs", "SimulationOutputs"):
        assert schemas[union]["properties"]["SimulationType"]["enum"] == names
        assert len(schemas[union]["oneOf"]) == len(names)


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
