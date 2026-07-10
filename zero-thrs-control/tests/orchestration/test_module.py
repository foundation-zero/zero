from datetime import datetime
from unittest.mock import Mock

from tests.orchestration.simples import (
    SimpleControl,
    SimpleControllerState,
    SimpleInOut,
    SimpleMode,
    SimpleParameters,
)
from thrs.classes.control import Control
from thrs.input_output.alarms import Alarm, BaseAlarms, Severity
from thrs.input_output.base import CombinedValues, Stamped, ThrsValues
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.orchestration.module import (
    CombinedAlarms,
    CombinedControl,
    CombinedModule,
    ModuleDescription,
)


class MockParametersModel(ThrsValues):
    setpoint: float = 25.0
    gain: float = 1.0


class MockSimulationInputs(ThrsValues):
    input_value: float = 10.0


class MockSimulationOutputs(ThrsValues):
    output_value: float = 20.0


class TestCombinedControl:
    def test_initial(self):
        time_fn = Mock(return_value=datetime.now())
        modules = {"module1": SimpleControl(SimpleParameters(), time_fn)}

        combined_control = CombinedControl(modules, time_fn)
        control_values, controller_state = combined_control.initial()

        assert isinstance(control_values, CombinedValues)
        assert "module1" in control_values.values
        assert isinstance(controller_state, CombinedValues)
        assert "module1" in controller_state.values

    def test_control(self):
        time_fn = Mock(return_value=datetime.now())
        mock_control = Mock(
            spec=SimpleControl,
            initial=Mock(return_value=(SimpleInOut.zero(), SimpleControllerState())),
        )
        mock_control.control.return_value = (
            SimpleInOut(
                go_with_the=FlowSensor(
                    flow=Stamped.stamp(20.0), temperature=Stamped.stamp(30.0)
                )
            ),
            SimpleControllerState(),
        )

        modules = {"module1": mock_control}

        combined_control = CombinedControl(modules, time_fn)
        combined_control.set_automation_mode("module1", True)

        sensor_values = CombinedValues(
            values={
                "module1": SimpleInOut(
                    go_with_the=FlowSensor(
                        flow=Stamped.stamp(30.0), temperature=Stamped.stamp(25.0)
                    )
                )
            }
        )

        control_values, controller_state = combined_control.control(sensor_values)

        assert isinstance(control_values, CombinedValues)
        assert "module1" in control_values.values
        assert isinstance(controller_state, CombinedValues)
        assert "module1" in controller_state.values
        mock_control.control.assert_called_once_with(sensor_values.values["module1"])

    def test_update_parameters(self):
        mock_control = Mock(
            spec=SimpleControl,
            initial=Mock(return_value=(SimpleInOut.zero(), SimpleControllerState())),
        )

        modules = {"module1": mock_control}
        time_fn = Mock(return_value=datetime.now())

        combined_control = CombinedControl(modules, time_fn)

        parameters = CombinedValues(values={"module1": SimpleParameters()})

        combined_control.update_parameters(parameters)
        mock_control.update_parameters.assert_called_once()


class TestCombinedAlarms:
    def test_check_empty_values(self):
        mock_alarms = Mock(spec=BaseAlarms)
        subs = {"module1": mock_alarms}

        combined_alarms = CombinedAlarms(subs)

        values = CombinedValues(values={})

        result = combined_alarms.check(values, values, values)

        assert result == []

    def test_check_with_alarms(self):
        mock_alarm = Alarm(
            code="Test", message="Test message", severity=Severity.WARNING
        )
        mock_alarms = Mock(spec=BaseAlarms)
        mock_alarms.check.return_value = [mock_alarm]

        subs = {"module1": mock_alarms}
        combined_alarms = CombinedAlarms(subs)

        values = CombinedValues(
            values={
                "module1": SimpleInOut(
                    go_with_the=FlowSensor(
                        flow=Stamped.stamp(30.0), temperature=Stamped.stamp(25.0)
                    )
                )
            }
        )

        parameters = CombinedValues(values={"module1": SimpleParameters()})

        result = combined_alarms.check(values, values, parameters)

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
            SimpleMode,
            SimpleControllerState,
            alarms_fn,
        )

        modules = {"module1": module_desc}

        combined_module = CombinedModule(modules)

        assert combined_module.modules == ["module1"]
        assert combined_module.control_values_for_module("module1") == SimpleInOut
        assert combined_module.parameters_for_module("module1") == SimpleParameters

    def test_sensor_values_clss(self):
        control_fn = Mock()
        alarms_fn = Mock()

        module_desc = ModuleDescription(
            SimpleInOut,
            SimpleInOut,
            SimpleParameters,
            control_fn,
            SimpleMode,
            SimpleControllerState,
            alarms_fn,
        )

        modules = {"module1": module_desc}

        nesting = CombinedModule(modules)

        assert nesting.sensor_values_clss is not None

    def test_control(self):
        mock_control_instance = Mock(
            spec=Control,
            initial=Mock(return_value=(SimpleInOut.zero(), SimpleControllerState())),
        )
        control_fn = Mock(return_value=mock_control_instance)
        alarms_fn = Mock()

        module_desc = ModuleDescription(
            SimpleInOut,
            SimpleInOut,
            SimpleParameters,
            control_fn,
            SimpleMode,
            SimpleControllerState,
            alarms_fn,
        )

        modules = {"module1": module_desc}

        nesting = CombinedModule(modules)

        parameters = CombinedValues(values={"module1": SimpleParameters()})

        time_fn = Mock(return_value=datetime.now())

        control = nesting.control(parameters, time_fn)

        assert isinstance(control, CombinedControl)
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
            SimpleMode,
            SimpleControllerState,
            alarms_fn,
        )

        modules = {"module1": module_desc}

        nesting = CombinedModule(modules)

        alarms = nesting.alarms()

        assert isinstance(alarms, CombinedAlarms)
        alarms_fn.assert_called_once()
