from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest import mock
from unittest.mock import AsyncMock, Mock, call

from tests.helpers.collector import PolarsCollector
from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.thrusters import (
    ThrustersAlarms,
    ThrustersControl,
    ThrustersControllerState,
    ThrustersParameters,
)
from thrs.control.switching import AutomationMode
from thrs.input_output.base import CombinedValues
from thrs.input_output.fmu_mapping import build_fmu_key_mapping
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.module import Module
from thrs.orchestration.simulation import Simulation, SimulationUnit
from thrs.runtime.descriptions.simulation import SIMULATION_INPUTS
from thrs.runtime.runners.control import ControlRunner
from thrs.runtime.runners.lockstep import LockstepRunner
from thrs.runtime.runners.simulator import SimulationRunner
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping, flatten_model_values
from thrs.simulation.models.fmu_paths import thrusters_path


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

        control = ThrustersControl(
            ThrustersParameters(),
            simulation.time,
            MachineStateLoggingServiceNoop(),
        )
        alarms = ThrustersAlarms()

        io_mapping = ThrsModelIoMapping(
            ThrustersSensorValues, ThrustersSimulationOutputs
        )
        collector = PolarsCollector()
        runner = SimulationTestRunner(simulation, simulation_inputs, control, alarms)
        runner.run(20, collector)
        frame = collector.result()
        inputs = io_mapping.generate_inputs(
            ThrustersControlValues.zero(), simulation_inputs
        )
        outputs = fmu.tick(
            inputs,
            timedelta(seconds=1),
        )
        mock_fmu_outputs = io_mapping.construct_outputs(
            inputs, outputs, simulation_inputs, datetime.now(UTC)
        )[2]

        assert frame is not None
        assert frame["time"][-1] - frame["time"][0] == timedelta(seconds=19)

        not_in_fmu = set(
            {
                **flatten_model_values(
                    ThrustersSensorValues.zero(),
                    fmu_key_mapping=build_fmu_key_mapping(
                        ThrustersSensorValues, fmu_only=False
                    ),
                ),
                **flatten_model_values(
                    ThrustersControllerState.zero(),
                    fmu_key_mapping=build_fmu_key_mapping(
                        ThrustersControllerState, fmu_only=False
                    ),
                ),
                **flatten_model_values(
                    simulation_inputs,
                    fmu_key_mapping=build_fmu_key_mapping(
                        ThrustersSimulationInputs, fmu_only=False
                    ),
                ),
            }
        ) - set(
            {
                **flatten_model_values(
                    ThrustersSensorValues.zero(),
                    fmu_key_mapping=build_fmu_key_mapping(
                        ThrustersSensorValues, fmu_only=True
                    ),
                ),
                **flatten_model_values(
                    simulation_inputs,
                    fmu_key_mapping=build_fmu_key_mapping(
                        ThrustersSimulationInputs, fmu_only=True
                    ),
                ),
            }
        )

        assert (
            set(frame.columns)
            == set(mock_fmu_outputs.keys()) | {"time", "control_mode"} | not_in_fmu
        )


async def test_lockstep_runner_ticks_and_publishes_channels():
    control_values = mock.sentinel.control
    controller_state = {}
    parameters = {}
    sensor_values = mock.sentinel.sensor

    combined_sensor_values = CombinedValues(values={"module": sensor_values})  # type: ignore
    combined_control_values = CombinedValues(values={"module": control_values})  # type: ignore

    control = Mock()
    control.initial.return_value = (control_values, controller_state)
    control.control.return_value = (control_values, controller_state)
    control.parameters = parameters
    control.mode = None
    control.manual_controls = control_values

    simulation = Mock()
    simulation.tick.return_value = SimpleNamespace(
        sensor_values=combined_sensor_values,
        simulation_inputs=SimpleNamespace(),
        simulation_outputs=SimpleNamespace(),
    )

    control_channels = Mock()
    control_channels.get_parameters.return_value = parameters
    control_channels.get_automation_modes.return_value = None
    control_channels.get_manual_controls.return_value = control_values
    control_channels.send_control_values = AsyncMock()
    control_channels.send_computed_values = AsyncMock()
    control_channels.send_controller_state = AsyncMock()
    control_channels.send_parameters = AsyncMock()
    control_channels.send_control_modes = AsyncMock()
    control_channels.send_manual_control = AsyncMock()

    simulation_channels = Mock()
    simulation_channels.get_simulation_inputs.return_value = None
    simulation_channels.send_sensor_values = AsyncMock()
    simulation_channels.send_simulation_inputs = AsyncMock()
    simulation_channels.send_simulation_outputs = AsyncMock()

    alarms = Mock()
    alarms.check.return_value = []

    module = Module("module", control, alarms, control_channels)
    module.set_automation_mode(AutomationMode(mode="automatic"))

    simulation_module = SimulationUnit(simulation, simulation_channels)
    runner = LockstepRunner([module], simulation_module)

    for _ in range(3):
        await runner.tick()

    assert control_channels.send_control_values.await_count == 3
    assert simulation_channels.send_sensor_values.await_count == 3
    assert control_channels.send_controller_state.await_count == 3
    assert control_channels.send_computed_values.await_count == 3
    assert simulation_channels.send_simulation_inputs.await_count == 3
    assert simulation_channels.send_simulation_outputs.await_count == 3
    assert control_channels.send_parameters.await_count == 3
    assert control_channels.send_manual_control.await_count == 3
    assert control_channels.send_control_modes.await_count == 3

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
    # TODO: Restore this when control_runner does not need to wrap a switching control around the actual control
    # control.update_manual_controls.assert_has_calls(
    #     [call(control_values), call(control_values), call(control_values)]
    # )
    alarms.check.assert_has_calls(
        [
            call(sensor_values, control_values, parameters),
            call(sensor_values, control_values, parameters),
            call(sensor_values, control_values, parameters),
        ]
    )

    control_channels.send_control_values.assert_has_awaits(
        [call(control_values), call(control_values), call(control_values)]
    )
    control_channels.send_computed_values.assert_has_awaits(
        [call(sensor_values), call(sensor_values), call(sensor_values)]
    )
    simulation_channels.send_sensor_values.assert_has_awaits(
        [
            call(combined_sensor_values),
            call(combined_sensor_values),
            call(combined_sensor_values),
        ]
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
    control_channels.send_parameters.assert_has_awaits(
        [call(parameters), call(parameters), call(parameters)]
    )
    control_channels.send_manual_control.assert_has_awaits(
        [call(control_values), call(control_values), call(control_values)]
    )


async def test_control_runner_ticks_and_uses_channels():
    control_values = mock.sentinel.control
    controller_state = {}
    parameters = {}
    sensor_values = {"something": True}

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
    channels.get_manual_controls.return_value = mock.sentinel.control_new
    channels.get_sensor_values.return_value = sensor_values
    channels.send_computed_values = AsyncMock()
    channels.send_control_values = AsyncMock()
    channels.send_controller_state = AsyncMock()
    channels.send_parameters = AsyncMock()
    channels.send_control_modes = AsyncMock()
    channels.send_manual_control = AsyncMock()

    alarms = Mock()
    alarms.check.return_value = []

    module = Module("module", control, alarms, channels)
    module.set_automation_mode(AutomationMode(mode="automatic"))

    runner = ControlRunner([module], mock_liveness)

    for _ in range(2):
        await runner.tick()

    assert mock_liveness.signal.call_count == 2

    assert channels.get_sensor_values.call_count == 2
    assert channels.send_computed_values.await_count == 2
    assert control.control.call_count == 2
    assert alarms.check.call_count == 2

    assert control.update_parameters.call_count == 2
    assert module._control._manual_control._control_values == mock.sentinel.control_new

    assert channels.send_control_values.await_count == 2
    assert channels.send_controller_state.await_count == 2
    assert channels.send_parameters.await_count == 2
    assert channels.send_control_modes.await_count == 2
    assert channels.send_manual_control.await_count == 2

    channels.send_computed_values.assert_has_awaits(
        [call(sensor_values), call(sensor_values)]
    )
    channels.send_control_values.assert_has_awaits(
        [call(control_values), call(control_values)]
    )
    channels.send_controller_state.assert_has_awaits(
        [call(controller_state), call(controller_state)]
    )
    channels.send_parameters.assert_has_awaits([call(parameters), call(parameters)])
    channels.send_manual_control.assert_has_awaits(
        [call(mock.sentinel.control_new), call(mock.sentinel.control_new)]
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
        simulation_inputs=simulation_inputs,
        simulation_outputs=simulation_outputs,
    )

    channels = Mock()
    channels.get_control_values.return_value = control_values
    channels.get_simulation_inputs.return_value = simulation_inputs
    channels.wait_for_control_values = AsyncMock()
    channels.send_sensor_values = AsyncMock()
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

    assert channels.send_sensor_values.await_count == 4
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
    channels.send_sensor_values.assert_has_awaits(
        [
            call(sensor_values),
            call(sensor_values),
            call(sensor_values),
            call(sensor_values),
        ]
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
