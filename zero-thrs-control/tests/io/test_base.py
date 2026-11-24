from datetime import UTC, datetime

from pydantic import ValidationError
from pytest import raises

from thrs.control.state import ControlMode
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.input_output.definitions.simulation import HeatSource
from thrs.input_output.definitions.wire_context import WireContext


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


class ValuesWithList(ThrsValues):
    single: FlowSensor
    many: list[FlowSensor]
    scalar: float


def _flow_sensor(flow: float, temperature: float) -> FlowSensor:
    return FlowSensor(flow=Stamped.stamp(flow), temperature=Stamped.stamp(temperature))


def _values(offset: float) -> ValuesWithList:
    return ValuesWithList(
        single=_flow_sensor(1.0 + offset, 2.0 + offset),
        many=[_flow_sensor(3.0 + offset, 4.0 + offset)],
        scalar=5.0 + offset,
    )


def test_update_in_place_keeps_component_identity():
    target = _values(0.0)
    single, listed = target.single, target.many[0]

    target.update_in_place(_values(10.0))

    assert target.single is single
    assert target.many[0] is listed
    assert single.flow.value == 11.0
    assert listed.temperature.value == 14.0
    assert target.scalar == 15.0


def test_update_in_place_takes_over_timestamps():
    target = _values(0.0)
    source = _values(10.0)

    target.update_in_place(source)

    assert target.single.flow.timestamp == source.single.flow.timestamp


def test_update_in_place_does_not_alias_source():
    target = _values(0.0)
    source = _values(10.0)

    target.update_in_place(source)
    source.single.flow = Stamped.stamp(99.0)

    assert target.single.flow.value == 11.0


def test_update_in_place_rejects_mismatched_list_length():
    target = _values(0.0)
    source = _values(10.0)
    source.many = [*source.many, _flow_sensor(0.0, 0.0)]

    with raises(ValueError):
        target.update_in_place(source)


def test_a_set_value_without_timestamp_is_stamped_on_arrival():
    before = datetime.now(UTC)

    stamped = Stamped[float].model_validate({"Value": 0.3}, context=WireContext.SET)

    assert stamped.value == 0.3
    assert before <= stamped.timestamp <= datetime.now(UTC)


def test_a_set_value_keeps_its_timestamp():
    stamped = Stamped[float].model_validate(
        {"Value": 0.3, "TimeStamp": "2026-11-19T10:00:00Z"}, context=WireContext.SET
    )

    assert stamped.timestamp == datetime(2026, 11, 19, 10, tzinfo=UTC)


def test_a_value_outside_a_set_needs_a_timestamp():
    with raises(ValidationError):
        Stamped[float].model_validate({"Value": 0.3})
    with raises(ValidationError):
        Stamped[float].model_validate({"Value": 0.3}, context=WireContext.ACTUATED)
