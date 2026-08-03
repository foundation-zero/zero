from thrs.classes.control import ControlMode
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.input_output.definitions.simulation import HeatSource


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
