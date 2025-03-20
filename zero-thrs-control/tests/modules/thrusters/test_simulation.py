from datetime import datetime, timedelta
from pathlib import Path

from pytest import fixture
from input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationOutputs,
)
from orchestration.collector import PolarsCollector
from orchestration.executor import SimulationExecutor
from orchestration.interfacer import Interfacer
from orchestration.simulator import Simulator, SimulatorModel

@fixture
def executor(io_mapping, simulation_inputs):
    return SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=1)
    )


async def test_interfacer(executor, io_mapping, simulation_inputs, thrusters_control):
    collector = PolarsCollector()
    interfacer = Interfacer(thrusters_control, executor)
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


async def test_simulation(simulation_inputs, thrusters_control):

    thrusters_model = SimulatorModel(
        fmu_path=str(
            Path(__file__).resolve().parent.parent.parent.parent
            / "src/simulation/models/thrusters/thruster_moduleV6.fmu"
        ),
        sensor_values_cls=ThrustersSensorValues,
        control_values_cls=ThrustersControlValues,
        simulation_outputs_cls=ThrustersSimulationOutputs,
        simulation_inputs=simulation_inputs,
        control = thrusters_control)
    
    simulation = Simulator(thrusters_model)

    result = await simulation.run(20)

    assert result is not None
    assert result["time"].len() == 20
