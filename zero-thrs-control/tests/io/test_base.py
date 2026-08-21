from typing import Annotated

from thrs.classes.control import ControlMode
from thrs.input_output.base import (
    FieldLeaf,
    Payload,
    Stamped,
    ThrsValues,
    component_meta,
    walk_fields,
)
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.input_output.definitions.simulation import HeatSource
from thrs.input_output.definitions.units import Ratio


class SimpleInputs(ThrsValues):
    a: HeatSource


def test_flow_sensor():
    message = """{
        "flow": {
            "value": 12.12,
            "has-value": true,
            "is-valid": true,
            "timestamp": "2025-01-21T08:49:03.6735253Z"
        },
        "temperature": {
            "value": 17.12,
            "has-value": true,
            "is-valid": true,
            "timestamp": "2025-01-21T08:49:03.6735253Z"
        }
    }"""
    parsed_message = FlowSensor.model_validate_json(message)
    assert parsed_message.temperature.value == 17.12


def test_control_mode_str():
    class TestSubMode(ControlMode):
        mode: str

    class TestMode(ControlMode):
        mode: str
        submode: TestSubMode

        @property
        def some_property(self):
            return "some value"

    class EmptyMode(ControlMode):
        pass

    mode = TestMode(mode="mode", submode=TestSubMode(mode="mode"))
    empty_mode = EmptyMode()

    assert str(mode) == "mode, submode: mode"
    assert str(empty_mode) == ""


def test_json_dump():
    inputs = SimpleInputs(
        a=HeatSource(heat_flow=Stamped.stamp(1.0)),
    )

    class Test(ThrsValues):
        inputs: SimpleInputs

    model = Test(inputs=inputs)
    json = model.model_dump_json()
    assert model == Test.model_validate_json(json)


# ---------------------------------------------------------------------------
# walk_fields tests
# ---------------------------------------------------------------------------


class _Valve(ThrsValues, Payload):
    setpoint: Stamped[Ratio]


class _SubSensorValues(ThrsValues):
    field_sub: _Valve


class _SensorValues(ThrsValues):
    field_override: Annotated[_Valve, component_meta(topic_override="some_topic/bla")]
    field_direct: _Valve
    sub_model: _SubSensorValues


def test_walk_fields_topics():
    leaves = walk_fields(_SensorValues, "base_topic")
    topics = [leaf.topic for leaf in leaves]
    assert topics == [
        "base_topic/some_topic/bla",
        "base_topic/field-direct",
        "base_topic/sub-model/field-sub",
    ]


def test_walk_fields_is_payload():
    leaves = walk_fields(_SensorValues, "base_topic")
    assert all(leaf.is_payload for leaf in leaves)


def test_walk_fields_annotation():
    leaves = walk_fields(_SensorValues, "base_topic")
    assert all(leaf.annotation is _Valve for leaf in leaves)


def test_walk_fields_field_paths():
    leaves = walk_fields(_SensorValues, "base_topic")
    assert leaves[0].field_path == ("field_override",)
    assert leaves[1].field_path == ("field_direct",)
    assert leaves[2].field_path == ("sub_model", "field_sub")


def test_walk_fields_scalar():
    class _ScalarModel(ThrsValues):
        temperature: float

    leaves = walk_fields(_ScalarModel, "vessel/sensor")
    assert len(leaves) == 1
    leaf = leaves[0]
    assert leaf.topic == "vessel/sensor/temperature"
    assert leaf.field_path == ("temperature",)
    assert leaf.is_payload is False


def test_walk_fields_flat_returns_field_leaf_type():
    leaves = walk_fields(_SensorValues, "base_topic")
    assert all(isinstance(leaf, FieldLeaf) for leaf in leaves)

