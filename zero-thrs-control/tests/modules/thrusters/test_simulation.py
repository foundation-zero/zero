from datetime import datetime, timedelta
from pathlib import Path

from pytest import fixture
import pytest
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
    assert set(frame.columns) == set(mock_fmu_outputs.keys()) | {"time"}
    assert frame["time"][-1] - frame["time"][0] == timedelta(seconds=19)


async def test_simulation(simulation_inputs, control, alarms):

    thrusters_model = SimulatorModel(
        fmu_path=str(
            Path(__file__).resolve().parent.parent.parent.parent
            / "src/simulation/models/thrusters/thruster_moduleV10_1.fmu"
        ),
        sensor_values_cls=ThrustersSensorValues,
        control_values_cls=ThrustersControlValues,
        simulation_outputs_cls=ThrustersSimulationOutputs,
        simulation_inputs=simulation_inputs,
        control=control,
        alarms=alarms,
    )

    simulation = Simulator(thrusters_model)

    result = await simulation.run(20)

    assert result is not None
    assert result["time"].len() == 20


@fixture(params=list(simulator_input_field_setters(ThrustersSimulationInputs)))
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_thrusters_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(
        str(
            Path(__file__).resolve().parent.parent.parent.parent
            / "src/simulation/models/thrusters/thruster_moduleV10_1.fmu"
        )
    ) as fmu:
        mapping = IoMapping(
            fmu,
            ThrustersSensorValues,
            ThrustersSimulationOutputs,
        )

        with pytest.raises(Exception):
            mapping.tick(
                control.initial(datetime.now()).values,
                incorrect_simulation_inputs,
                datetime.now(),
                timedelta(seconds=1),
            )
