import pytest
from datetime import datetime
from unittest.mock import Mock
from tests.orchestration.simples import (
    SimpleControl,
    SimpleInOut,
    SimpleParameters,
    SimpleSimulationInputs,
    SimpleSimulationOutputs,
)
from thrs.input_output.base import Stamped, ThrsModel, NestedValues
from thrs.input_output.alarms import Alarm, BaseAlarms, Severity
from thrs.classes.control import Control, ControlResult

from thrs.input_output.definitions.sensor import FlowSensor
from thrs.orchestration.module import (
    ModuleDescription,
    PartialMqttMapping,
    DirectMqttMapping,
    NestedMqttMapping,
    NestedControl,
    NestedAlarms,
    ModuleNesting,
)


class MockParametersModel(ThrsModel):
    setpoint: float = 25.0
    gain: float = 1.0


class MockSimulationInputs(ThrsModel):
    input_value: float = 10.0


class MockSimulationOutputs(ThrsModel):
    output_value: float = 20.0


class TestPartialMqttMapping:
    def test_split_to_topics_without_suffix(self):
        mapping = PartialMqttMapping(SimpleInOut)
        flow_sensor = FlowSensor(
            flow=Stamped.stamp(10.0), temperature=Stamped.stamp(25.0)
        )
        model = SimpleInOut(go_with_the=flow_sensor)

        topics = mapping.split_to_topics(model)

        assert "go-with-the" in topics
        topic = topics["go-with-the"]
        assert FlowSensor.model_validate_json(topic) == flow_sensor

    def test_split_to_topics_with_suffix(self):
        mapping = PartialMqttMapping(SimpleInOut, "sensors")
        flow_sensor = FlowSensor(
            flow=Stamped.stamp(10.0), temperature=Stamped.stamp(25.0)
        )
        model = SimpleInOut(go_with_the=flow_sensor)

        topics = mapping.split_to_topics(model)

        assert "go-with-the/sensors" in topics
        topic = topics["go-with-the/sensors"]
        assert FlowSensor.model_validate_json(topic) == flow_sensor

    def test_has_without_suffix(self):
        mapping = PartialMqttMapping(SimpleInOut)

        assert mapping.has("go-with-the")
        assert not mapping.has("nonexistent")

    def test_has_with_suffix(self):
        mapping = PartialMqttMapping(SimpleInOut, "sensors")

        assert mapping.has("go-with-the/sensors")
        assert not mapping.has("go-with-the")

    def test_subscribe_topic(self):
        mapping_no_suffix = PartialMqttMapping(SimpleInOut)
        mapping_with_suffix = PartialMqttMapping(SimpleInOut, "sensors")

        assert mapping_no_suffix.subscribe_topic() == "+"
        assert mapping_with_suffix.subscribe_topic() == "+/sensors"

    def test_builder(self):
        mapping = PartialMqttMapping(SimpleInOut)
        builder = mapping.builder()

        flow_sensor = FlowSensor(
            flow=Stamped.stamp(15.0), temperature=Stamped.stamp(30.0)
        )
        builder.input("go-with-the", flow_sensor.model_dump_json(by_alias=True))
        assert builder.result() == SimpleInOut(go_with_the=flow_sensor)


class TestDirectMqttMapping:
    def test_split_to_topics(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")
        model = SimpleInOut(
            go_with_the=FlowSensor(
                flow=Stamped.stamp(25.0), temperature=Stamped.stamp(1.2)
            )
        )
        topics = mapping.split_to_topics(model)

        assert "sensors/data" in topics
        assert topics["sensors/data"] == model.model_dump_json(by_alias=True)

    def test_has(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")

        assert mapping.has("sensors/data")
        assert not mapping.has("other/topic")

    def test_subscribe_topic(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")

        assert mapping.subscribe_topic() == "sensors/data"

    def test_builder_not_implemented(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")
        with pytest.raises(NotImplementedError):
            mapping.builder()


class TestNestedMqttMapping:
    def test_split_to_topics(self):
        clss = {"module1": SimpleInOut}
        mapping = NestedMqttMapping(clss)
        flow_sensor = FlowSensor(
            flow=Stamped.stamp(25.0), temperature=Stamped.stamp(1.2)
        )
        nested_values = NestedValues(
            values={"module1": SimpleInOut(go_with_the=flow_sensor)}
        )

        topics = mapping.split_to_topics(nested_values)

        assert "module1/go-with-the" in topics
        assert topics["module1/go-with-the"] == flow_sensor.model_dump_json(
            by_alias=True
        )

    def test_has(self):
        clss = {"module1": SimpleInOut}
        mapping = NestedMqttMapping(clss)

        assert mapping.has("module1/go-with-the")
        assert not mapping.has("module2/go-with-the")

    def test_subscribe_topic(self):
        clss = {"module1": SimpleInOut}
        mapping_no_suffix = NestedMqttMapping(clss)
        mapping_with_suffix = NestedMqttMapping(clss, "sensors")

        assert mapping_no_suffix.subscribe_topic() == "+/+"
        assert mapping_with_suffix.subscribe_topic() == "+/+/sensors"

    def test_builder(self):
        clss = {"module1": SimpleInOut}
        mapping = NestedMqttMapping(clss)
        builder = mapping.builder()

        flow_sensor = FlowSensor(
            flow=Stamped.stamp(50.0), temperature=Stamped.stamp(5.0)
        )
        builder.input("module1/go-with-the", flow_sensor.model_dump_json(by_alias=True))
        result = builder.result()
        assert result == NestedValues({"module1": SimpleInOut(go_with_the=flow_sensor)})


class TestNestedControl:
    def test_initial(self):
        time_fn = Mock(return_value=datetime.now())
        modules = {"module1": SimpleControl(SimpleParameters(), time_fn)}

        nested_control = NestedControl(modules, time_fn)
        result = nested_control.initial()

        assert isinstance(result.values, NestedValues)
        assert "module1" in result.values.values

    def test_control(self):
        time_fn = Mock(return_value=datetime.now())
        mock_control = Mock(spec=SimpleControl)
        mock_control.control.return_value = ControlResult(
            values=SimpleInOut(
                go_with_the=FlowSensor(
                    flow=Stamped.stamp(20.0), temperature=Stamped.stamp(30.0)
                )
            ),
            timestamp=datetime.now(),
        )

        modules = {"module1": mock_control}

        nested_control = NestedControl(modules, time_fn)
        nested_control.set_automation_mode("module1", True)

        sensor_values = NestedValues(
            values={
                "module1": SimpleInOut(
                    go_with_the=FlowSensor(
                        flow=Stamped.stamp(30.0), temperature=Stamped.stamp(25.0)
                    )
                )
            }
        )

        result = nested_control.control(sensor_values)

        assert isinstance(result.values, NestedValues)
        assert "module1" in result.values.values
        mock_control.control.assert_called_once_with(sensor_values.values["module1"])

    def test_update_parameters(self):
        mock_control = Mock(spec=SimpleControl)

        modules = {"module1": mock_control}
        time_fn = Mock(return_value=datetime.now())

        nested_control = NestedControl(modules, time_fn)

        parameters = NestedValues(values={"module1": SimpleParameters()})

        nested_control.update_parameters(parameters)

        mock_control.update_parameters.assert_called_once()


class TestNestedAlarms:
    def test_check_empty_values(self):
        mock_alarms = Mock(spec=BaseAlarms)
        subs = {"module1": mock_alarms}

        nested_alarms = NestedAlarms(subs)

        sensor_values = NestedValues(values={})
        control_values = NestedValues(values={})

        result = nested_alarms.check(sensor_values, control_values)

        assert result == []

    def test_check_with_alarms(self):
        mock_alarm = Alarm(code="Test", severity=Severity.WARNING)
        mock_alarms = Mock(spec=BaseAlarms)
        mock_alarms.check.return_value = [mock_alarm]

        subs = {"module1": mock_alarms}
        nested_alarms = NestedAlarms(subs)

        values = NestedValues(
            values={
                "module1": SimpleInOut(
                    go_with_the=FlowSensor(
                        flow=Stamped.stamp(30.0), temperature=Stamped.stamp(25.0)
                    )
                )
            }
        )

        result = nested_alarms.check(values, values)

        assert len(result) == 1
        assert result[0] == mock_alarm


class TestModuleNesting:
    def test_properties(self):
        control_fn = Mock()
        alarms_fn = Mock()

        module_desc = ModuleDescription(
            SimpleInOut,
            SimpleInOut,
            SimpleParameters,
            control_fn,
            alarms_fn,
        )

        modules = {"module1": module_desc}

        nesting = ModuleNesting(
            modules, SimpleSimulationInputs, SimpleSimulationOutputs
        )

        assert nesting.modules == ["module1"]
        assert nesting.simulation_inputs_cls == SimpleSimulationInputs
        assert nesting.simulation_outputs_cls == SimpleSimulationOutputs
        assert nesting.control_values_for_module("module1") == SimpleInOut
        assert nesting.parameters_for_module("module1") == SimpleParameters

    def test_io_mapping(self):
        control_fn = Mock()
        alarms_fn = Mock()

        module_desc = ModuleDescription(
            SimpleInOut,
            SimpleInOut,
            SimpleParameters,
            control_fn,
            alarms_fn,
        )

        modules = {"module1": module_desc}

        nesting = ModuleNesting(
            modules, SimpleSimulationInputs, SimpleSimulationOutputs
        )

        io_mapping = nesting.io_mapping()
        assert io_mapping is not None

    def test_control(self):
        mock_control_instance = Mock(spec=Control)
        control_fn = Mock(return_value=mock_control_instance)
        alarms_fn = Mock()

        module_desc = ModuleDescription(
            SimpleInOut,
            SimpleInOut,
            SimpleParameters,
            control_fn,
            alarms_fn,
        )

        modules = {"module1": module_desc}

        nesting = ModuleNesting(
            modules, SimpleSimulationInputs, SimpleSimulationOutputs
        )

        parameters = NestedValues(values={"module1": SimpleParameters()})

        time_fn = Mock(return_value=datetime.now())

        control = nesting.control(parameters, time_fn)

        assert isinstance(control, NestedControl)
        control_fn.assert_called_once()

    def test_alarms(self):
        mock_alarms_instance = Mock(spec=BaseAlarms)
        control_fn = Mock()
        alarms_fn = Mock(return_value=mock_alarms_instance)

        module_desc = ModuleDescription(
            SimpleInOut,
            SimpleInOut,
            SimpleParameters,
            control_fn,
            alarms_fn,
        )

        modules = {"module1": module_desc}

        nesting = ModuleNesting(
            modules, SimpleSimulationInputs, SimpleSimulationOutputs
        )

        alarms = nesting.alarms()

        assert isinstance(alarms, NestedAlarms)
        alarms_fn.assert_called_once()
