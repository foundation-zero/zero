from __future__ import annotations

from typing import Annotated
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import computed_field
from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.classes.control import ControlMode
from thrs.control.switching import SwitchingControlMode
from thrs.input_output.base import ThrsValues
from thrs.orchestration.comms import (
    DirectMqttMapping,
    MergedModuleMqttMapping,
    ModuleMqttMapping,
    PartialMqttMapping,
)
from thrs.orchestration.config import Config
from thrs.orchestration.module import ModuleDescription
from thrs.orchestration.simulation import SimulationDescription
from thrs.runtime.descriptions.simulation import Mode
from thrs.runtime.messages import SimulationStatusMessage
from thrs.spec.recording_connector import (
    RecordingConnector,
    TopicMapping,
    _describe_mapping,
    _field_annotation,
    _strip_none,
    collect_topics,
)


class SampleStatus(ThrsValues):
    code: int


class CustomMode(ControlMode):
    pass


class DummyPayloadModel(ThrsValues):
    speed: int
    temperature: float | None

    @computed_field
    @property
    def is_active(self) -> bool:
        return self.speed > 0


# ---------------------------------------------------------------------------
# Type Introspection Helper Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        (int | None, int),
        (str | None, str),
        (str, str),
        (list[str], list[str]),
        (Annotated[int | None, "meta"], int),
    ],
)
def test_strip_none(annotation: type, expected: type):
    assert _strip_none(annotation) == expected


def test_strip_none_errors_on_multi_type_unions():
    with pytest.raises(ValueError):
        _strip_none(int | str | None)


def test_field_annotation_with_standard_field():
    field = FieldInfo(annotation=int | None)  # type: ignore
    assert _field_annotation(field) is int


def test_field_annotation_with_computed_field():
    computed_info = Mock(
        spec=ComputedFieldInfo, return_type=str | None, wrapped_property=property()
    )
    assert _field_annotation(computed_info) is str


# ---------------------------------------------------------------------------
# Mapping Description Tests
# ---------------------------------------------------------------------------


def test_describe_mapping_partial_skips_ignored_prefix(settings: Config):
    mapping = PartialMqttMapping(
        DummyPayloadModel, settings.mqtt_devices_topic_prefix, "module"
    )

    result = _describe_mapping(settings, mapping)
    assert result == []


def test_describe_mapping_partial_standard_fields(settings: Config):
    mapping = PartialMqttMapping(DummyPayloadModel, "system/sensors", "module")

    described = _describe_mapping(settings, mapping)

    # DummyPayloadModel standard fields: speed (int), temperature (float | None -> float)
    topics = [item[0] for item in described]
    types = [item[1] for item in described]

    assert topics == [
        "system/sensors/module/speed",
        "system/sensors/module/temperature",
    ]
    assert types == [int, float]


def test_describe_mapping_partial_computed_fields_only(settings: Config):
    mapping = PartialMqttMapping(
        DummyPayloadModel, "system/status", "module", only_computed_fields=True
    )

    described = _describe_mapping(settings, mapping)

    assert len(described) == 1
    assert described[0][0] == "system/status/module/is-active"
    assert described[0][1] is bool


def test_describe_mapping_direct(settings: Config):
    mapping = DirectMqttMapping(DummyPayloadModel, "devices/actuator/control-mode")

    described = _describe_mapping(settings, mapping)

    assert len(described) == 1
    assert described[0][0] == "devices/actuator/control-mode"
    assert described[0][1] == DummyPayloadModel
    assert described[0][2] is None


def test_describe_mapping_module_recursive(settings: Config):
    module_mapping = ModuleMqttMapping(
        {"topic1": SampleStatus, "topic2": SampleStatus}, PartialMqttMapping
    )

    described = _describe_mapping(settings, module_mapping)
    topics = [item[0] for item in described]
    assert topics == ["/500000-thrs/topic1/code", "/500000-thrs/topic2/code"]


def test_describe_mapping_merged_module_returns_empty(settings: Config):
    mapping = MergedModuleMqttMapping({}, {}, "")
    assert _describe_mapping(settings, mapping) == []  # type: ignore[arg-type]


def test_describe_mapping_unsupported_type_raises(settings: Config):
    with pytest.raises(TypeError, match="Don't know how to describe"):
        _describe_mapping(settings, object())  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# RecordingConnector Tests
# ---------------------------------------------------------------------------


def test_recording_connector_register_listener(settings: Config):
    connector = RecordingConnector(settings)
    receiver = DirectMqttMapping(DummyPayloadModel, "devices/actuator/control-mode")

    connector._register_listener(receiver)

    assert len(connector.topics) == 1
    topic = connector.topics[0]
    assert topic == TopicMapping(
        topic="devices/actuator/control-mode",
        payload_type=DummyPayloadModel,
        direction="receive",
        component_type=None,
        qos=None,
        retain=False,
    )


def test_recording_connector_create_publisher(settings: Config):
    connector = RecordingConnector(settings)
    sender = DirectMqttMapping(DummyPayloadModel, "devices/actuator/control-mode")

    connector._create_publisher(sender, qos=2, retain=True)

    assert len(connector.topics) == 1
    topic = connector.topics[0]
    assert topic == TopicMapping(
        topic="devices/actuator/control-mode",
        payload_type=DummyPayloadModel,
        direction="send",
        component_type=None,
        qos=2,
        retain=True,
    )


# ---------------------------------------------------------------------------
# collect_topics Orchestration Tests
# ---------------------------------------------------------------------------


def test_collect_topics_wires_channels(settings: Config):
    mode = Mode(
        name="thrs",
        control_modules={
            "test": ModuleDescription(
                sensor_values_cls=ThrsValues,
                control_values_cls=ThrsValues,
                parameters_cls=ThrsValues,
                control=None,  # type: ignore
                control_mode_cls=ThrsValues,
                controller_state_cls=ThrsValues,
                alarms=None,  # type: ignore
            ),
        },
        simulation_description=SimulationDescription(ThrsValues, None, ThrsValues()),  # type: ignore
    )
    mock_sim_desc = MagicMock()
    mock_sim_desc.simulation_inputs = DummyPayloadModel(speed=1, temperature=20.0)
    mock_sim_desc.simulation_outputs_cls = SampleStatus

    with patch.object(
        RecordingConnector,
        "_register_listener",
        side_effect=lambda r: None,
    ):
        topics = collect_topics(settings, mode)

    assert isinstance(topics, list)
    assert topics == [
        TopicMapping(
            topic="test_controller_topic/test/parameters",
            payload_type=ThrsValues,
            direction="send",
            component_type=None,
            qos=1,
            retain=False,
        ),
        TopicMapping(
            topic="test_controller_topic/test/control-mode",
            payload_type=SwitchingControlMode[ThrsValues],
            direction="send",
            component_type=None,
            qos=1,
            retain=False,
        ),
        TopicMapping(
            topic="test_controller_topic/test/manual-values",
            payload_type=ThrsValues,
            direction="send",
            component_type=None,
            qos=1,
            retain=False,
        ),
        TopicMapping(
            topic="test_simulation_topic/simulation-inputs",
            payload_type=ThrsValues,
            direction="send",
            component_type=None,
            qos=0,
            retain=False,
        ),
        TopicMapping(
            topic="test_simulation_topic/simulation-outputs",
            payload_type=ThrsValues,
            direction="send",
            component_type=None,
            qos=0,
            retain=False,
        ),
        TopicMapping(
            topic="test_simulation_topic/status",
            payload_type=SimulationStatusMessage,
            direction="send",
            component_type=None,
            qos=1,
            retain=True,
        ),
    ]
