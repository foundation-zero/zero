from datetime import UTC, datetime, timedelta
from functools import partial
from types import SimpleNamespace
from unittest import mock
from unittest.mock import AsyncMock, Mock, call

from tests.helpers.collector import PolarsCollector
from tests.helpers.simulation_runner import (
    SimulationTestRunner,
    flatten_controller_state,
)
from tests.orchestration.simples import simple_control_values, simple_controller_state
from thrs.control.modules.thrusters.control import ThrustersAlarms, ThrustersControl
from thrs.control.modules.thrusters.io import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationOutputs,
)
from thrs.control.modules.thrusters.state import (
    ThrustersParameters,
)
from thrs.control.state import AutomationMode
from thrs.input_output.base import CombinedValues, Stamped
from thrs.input_output.definitions.system import AmcsControlMode, ControlMode
from thrs.input_output.fmu_mapping import build_fmu_key_mapping
from thrs.orchestration.module import Module
from thrs.orchestration.simulation import Simulation, SimulationUnit
from thrs.persistence.engine import NoopPersistentEngine
from thrs.persistence.manager import PersistManager
from thrs.runtime.descriptions.simulation import SIMULATION_INPUTS
from thrs.runtime.runners.control import ControlRunner
from thrs.runtime.runners.lockstep import LockstepRunner
from thrs.runtime.runners.simulator import SimulationRunner
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping, flatten_model_values
from thrs.simulation.models.fmu_paths import thrusters_path


def _mock_description(control: Mock, alarms: Mock) -> Mock:
    """Stand-in ModuleDescription whose factories return the same mock control
    and alarms, so engaging automatic rebuilds without needing real classes."""
    description = Mock()
    description.control.return_value = control
    description.alarms.return_value = alarms
    return description


def test_simulation_test_runner():
    simulation_inputs = SIMULATION_INPUTS["thrusters"]

    with Fmu(thrusters_path) as fmu:
        simulation = Simulation(
            ThrustersSensorValues,
            ThrustersSimulationOutputs,
            fmu,
            simulation_inputs,
            datetime.now(UTC),
            timedelta(seconds=1),
        )

        control = ThrustersControl(ThrustersParameters(), simulation.time)
        alarms = ThrustersAlarms()

        io_mapping = ThrsModelIoMapping(
            ThrustersSensorValues, ThrustersSimulationOutputs
        )
        collector = PolarsCollector()
        runner = SimulationTestRunner(simulation, simulation_inputs, control, alarms)
        _, _, controller_state = runner.run(20, collector)
        frame = collector.result()
        inputs = io_mapping.generate_inputs(
            ThrustersControlValues.zero(), simulation_inputs
        )
        outputs = fmu.tick(
            inputs,
            timedelta(seconds=1),
        )
        mock_fmu_outputs = io_mapping.construct_outputs(
            inputs,
            outputs,
            ThrustersControlValues.zero(),
            simulation_inputs,
            datetime.now(UTC),
        )[2]

        assert frame is not None
        assert frame["time"][-1] - frame["time"][0] == timedelta(seconds=19)

        all_keys = partial(build_fmu_key_mapping, fmu_only=False)
        not_in_fmu = {
            *flatten_model_values(ThrustersSensorValues.zero(), all_keys),
            *flatten_model_values(ThrustersControlValues.zero(), all_keys),
            *flatten_controller_state(controller_state),
            *flatten_model_values(simulation_inputs, all_keys),
        } - {
            *flatten_model_values(ThrustersSensorValues.zero(), build_fmu_key_mapping),
            *flatten_model_values(ThrustersControlValues.zero(), build_fmu_key_mapping),
            *flatten_model_values(simulation_inputs, build_fmu_key_mapping),
        }

        assert (
            set(frame.columns)
            == set(mock_fmu_outputs.keys()) | {"time", "control_mode"} | not_in_fmu
        )


async def test_lockstep_runner_ticks_and_publishes_channels():
    control_values = simple_control_values(flow=1.0)
    controller_state = simple_controller_state()
    parameters = mock.sentinel.parameters
    sensor_values = Mock(mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)))

    combined_sensor_values = CombinedValues(values={"module": sensor_values})
    combined_control_values = CombinedValues(values={"module": control_values})  # pyrefly: ignore[bad-assignment]

    control = Mock()
    control.initial.return_value = (control_values, controller_state)
    control.control.return_value = (control_values, controller_state)
    control.parameters = parameters
    control.mode = None
    control.manual_controls = control_values

    simulation = Mock()
    simulation.tick.return_value = SimpleNamespace(
        sensor_values=combined_sensor_values,
        control_values=combined_control_values,
        simulation_inputs=SimpleNamespace(),
        simulation_outputs=SimpleNamespace(),
    )

    control_channels = Mock()
    control_channels.get_parameters.return_value = parameters
    control_channels.get_automation_modes.return_value = None
    control_channels.get_manual_controls.return_value = control_values
    control_channels.get_control_values_set.return_value = None
    control_channels.send_control_values = AsyncMock()
    control_channels.send_computed_values = AsyncMock()
    control_channels.send_controller_state = AsyncMock()
    control_channels.send_actuated_control_values = AsyncMock()

    simulation_channels = Mock()
    simulation_channels.get_simulation_inputs.return_value = None
    simulation_channels.send_device_values = AsyncMock()
    simulation_channels.send_simulation_inputs = AsyncMock()
    simulation_channels.send_simulation_outputs = AsyncMock()

    alarms = Mock()
    alarms.check.return_value = []

    module = Module(
        "module",
        description=_mock_description(control, alarms),
        channels=control_channels,
        time_fn=datetime.now,
    )
    module.set_automation_mode(AutomationMode(mode="automatic"))

    simulation_module = SimulationUnit(simulation, simulation_channels)
    persistence = PersistManager(NoopPersistentEngine())
    runner = LockstepRunner([module], simulation_module, persistence)

    for _ in range(3):
        await runner.tick()

    assert control_channels.send_control_values.await_count == 3
    assert simulation_channels.send_device_values.await_count == 3
    assert control_channels.send_controller_state.await_count == 3
    assert control_channels.send_computed_values.await_count == 3
    assert simulation_channels.send_simulation_inputs.await_count == 3
    assert simulation_channels.send_simulation_outputs.await_count == 3
    assert control_channels.send_actuated_control_values.await_count == 3
    assert controller_state.automation_mode == AutomationMode(mode="automatic")
    assert controller_state.manual_values == control_values

    assert control.initial.call_count == 2
    assert simulation.tick.call_count == 3
    assert control.control.call_count == 3
    assert alarms.check.call_count == 3

    simulation.tick.assert_has_calls(
        [
            call(combined_control_values),
            call(combined_control_values),
            call(combined_control_values),
        ]
    )
    control.control.assert_has_calls(
        [
            call(sensor_values),
            call(sensor_values),
            call(sensor_values),
        ]
    )
    control.update_parameters.assert_has_calls(
        [call(parameters), call(parameters), call(parameters)]
    )
    alarms.check.assert_has_calls(
        [
            call(sensor_values, control_values, controller_state),
            call(sensor_values, control_values, controller_state),
            call(sensor_values, control_values, controller_state),
        ]
    )

    control_channels.send_control_values.assert_has_awaits(
        [call(control_values), call(control_values), call(control_values)]
    )
    control_channels.send_computed_values.assert_has_awaits(
        [call(sensor_values), call(sensor_values), call(sensor_values)]
    )
    assert (
        simulation_channels.send_device_values.await_args_list
        == [call(combined_sensor_values, combined_control_values)] * 3
    )

    expected_inputs = SimpleNamespace()
    expected_outputs = SimpleNamespace()
    simulation_channels.send_simulation_inputs.assert_has_awaits(
        [call(expected_inputs), call(expected_inputs), call(expected_inputs)]
    )
    simulation_channels.send_simulation_outputs.assert_has_awaits(
        [call(expected_outputs), call(expected_outputs), call(expected_outputs)]
    )

    control_channels.send_controller_state.assert_has_awaits(
        [call(controller_state), call(controller_state), call(controller_state)]
    )


async def test_control_runner_ticks_and_uses_channels():
    control_values = simple_control_values(flow=1.0)
    control_values_new = simple_control_values(flow=2.0)
    controller_state = simple_controller_state()
    parameters = mock.sentinel.parameters
    sensor_values = Mock(mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)))

    mock_liveness = Mock()

    control = Mock()
    control.initial.return_value = (control_values, controller_state)
    control.control.return_value = (control_values, controller_state)
    control.parameters = parameters
    control.mode = None
    control.manual_controls = control_values

    channels = Mock()
    channels.get_parameters.return_value = parameters
    channels.get_automation_modes.return_value = None
    channels.get_manual_controls.return_value = control_values_new
    channels.get_control_values_set.return_value = None
    channels.get_sensor_values.return_value = sensor_values
    channels.send_computed_values = AsyncMock()
    channels.send_control_values = AsyncMock()
    channels.send_controller_state = AsyncMock()
    channels.send_actuated_control_values = AsyncMock()

    alarms = Mock()
    alarms.check.return_value = []

    module = Module(
        "module",
        description=_mock_description(control, alarms),
        channels=channels,
        time_fn=datetime.now,
    )
    module.set_automation_mode(AutomationMode(mode="automatic"))

    persistence = PersistManager(NoopPersistentEngine())
    runner = ControlRunner([module], mock_liveness, persistence)

    for _ in range(2):
        await runner.tick()

    assert mock_liveness.signal.call_count == 2

    assert channels.get_sensor_values.call_count == 2
    assert channels.send_computed_values.await_count == 2
    assert control.control.call_count == 2
    assert alarms.check.call_count == 2

    assert control.update_parameters.call_count == 2

    assert channels.send_control_values.await_count == 2
    assert channels.send_controller_state.await_count == 2
    assert controller_state.automation_mode == AutomationMode(mode="automatic")
    assert channels.send_actuated_control_values.await_count == 2
    # Manual holds the UI value; automatic output is no longer tracked into it
    assert controller_state.manual_values == control_values_new

    channels.send_computed_values.assert_has_awaits(
        [call(sensor_values), call(sensor_values)]
    )
    channels.send_control_values.assert_has_awaits(
        [call(control_values), call(control_values)]
    )
    channels.send_controller_state.assert_has_awaits(
        [call(controller_state), call(controller_state)]
    )


async def test_simulation_runner_ticks_and_uses_inputs():
    control_values = {}
    simulation_inputs = SimpleNamespace()
    sensor_values = {}
    simulation_outputs = SimpleNamespace()

    mock_liveness = Mock()

    simulation = Mock()
    simulation.tick.return_value = SimpleNamespace(
        sensor_values=sensor_values,
        control_values=control_values,
        simulation_inputs=simulation_inputs,
        simulation_outputs=simulation_outputs,
    )

    channels = Mock()
    channels.get_control_values.return_value = control_values
    channels.get_simulation_inputs.return_value = simulation_inputs
    channels.wait_for_control_values = AsyncMock()
    channels.send_device_values = AsyncMock()
    channels.send_simulation_inputs = AsyncMock()
    channels.send_simulation_outputs = AsyncMock()

    simulation_module = SimulationUnit(simulation, channels)

    runner = SimulationRunner(simulation_module, mock_liveness)

    for _ in range(4):
        await runner.tick()

    assert mock_liveness.signal.call_count == 4

    assert channels.get_control_values.call_count == 4
    assert channels.wait_for_control_values.await_count == 0
    assert simulation.update_simulation_inputs.call_count == 4
    assert simulation.tick.call_count == 4

    assert channels.send_device_values.await_count == 4
    assert channels.send_simulation_inputs.await_count == 4
    assert channels.send_simulation_outputs.await_count == 4

    simulation.tick.assert_has_calls(
        [
            call(control_values),
            call(control_values),
            call(control_values),
            call(control_values),
        ]
    )
    assert (
        channels.send_device_values.await_args_list
        == [call(sensor_values, control_values)] * 4
    )
    channels.send_simulation_inputs.assert_has_awaits(
        [
            call(simulation_inputs),
            call(simulation_inputs),
            call(simulation_inputs),
            call(simulation_inputs),
        ]
    )
    channels.send_simulation_outputs.assert_has_awaits(
        [
            call(simulation_outputs),
            call(simulation_outputs),
            call(simulation_outputs),
            call(simulation_outputs),
        ]
    )
