from datetime import datetime, timedelta

from pytest import fixture
import pytest
from input_output.definitions.control import Valve
from input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from orchestration.collector import PolarsCollector
from orchestration.executor import SimulationExecutor
from orchestration.cycler import Cycler
from orchestration.simulator import Simulator, SimulatorModel
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping
from simulation.models.fmu_paths import thrusters_path
from tests.modules.helpers.simulation_inputs import simulator_input_field_setters


@fixture
def executor(io_mapping, simulation_inputs):
    return SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=1)
    )


async def test_interfacer(executor, io_mapping, simulation_inputs, control, alarms):
    collector = PolarsCollector()
    interfacer = Cycler(control, executor, alarms)
    await interfacer.run(20, collector)
    frame = collector.result()
    mock_fmu_outputs = io_mapping.tick(
        ThrustersControlValues.zero(),
        simulation_inputs,
        datetime.now(),
        timedelta(seconds=1),
    )[2]
    assert frame is not None
    assert set(frame.columns) == set(mock_fmu_outputs.keys()) | {"time", "control_mode"}
    assert frame["time"][-1] - frame["time"][0] == timedelta(seconds=19)


async def test_simulation(simulation_inputs, control, alarms):
    thrusters_model = SimulatorModel(
        fmu_path=thrusters_path,
        sensor_values_cls=ThrustersSensorValues,
        control_values_cls=ThrustersControlValues,
        simulation_outputs_cls=ThrustersSimulationOutputs,
        simulation_inputs=simulation_inputs,
        control=control,
        alarms=alarms,
    )

    with thrusters_model.executor() as executor:
        simulation = Simulator(thrusters_model, executor)

        result = await simulation.run(20)

        assert result is not None
        assert result["time"].len() == 20


@fixture(params=list(simulator_input_field_setters(ThrustersSimulationInputs)))
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_thrusters_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(thrusters_path) as fmu:
        mapping = IoMapping(
            fmu,
            ThrustersSensorValues,
            ThrustersSimulationOutputs,
        )

        control_values = control.initial(datetime.now()).values

        control_values.thrusters_pump_1.dutypoint.value = 1
        control_values.thrusters_mix_aft.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.thrusters_mix_fwd.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.thrusters_flowcontrol_aft.setpoint.value = Valve.OPEN
        control_values.thrusters_flowcontrol_fwd.setpoint.value = Valve.OPEN
        control_values.thrusters_pump_1.on.value = True

        with pytest.raises(Exception):
            for i in range(100):
                mapping.tick(
                    control._current_values,
                    incorrect_simulation_inputs,
                    datetime.now(),
                    timedelta(seconds=5),
                )
