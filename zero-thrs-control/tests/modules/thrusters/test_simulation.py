from datetime import datetime, timedelta
from pathlib import Path

from pytest import fixture
from control.modules.thrusters import ThrustersControl, ThrustersSetpoints
from input_output.base import Stamped
from input_output.definitions.simulation import Boundary, HeatSource, TemperatureBoundary
from input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from orchestration.collector import PolarsCollector
from orchestration.executor import SimulationExecutor
from orchestration.interfacer import Interfacer
from orchestration.simulator import Simulator, SimulatorModel
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping

@fixture
def simulation_inputs():
    return ThrustersSimulationInputs(
    thrusters_aft=HeatSource(heat_flow=Stamped.stamp(9000)),
    thrusters_fwd=HeatSource(heat_flow=Stamped.stamp(4300)),
    thrusters_seawater_supply=Boundary(
        temperature=Stamped.stamp(32), flow=Stamped.stamp(64)),
    thrusters_module_supply=TemperatureBoundary(temperature=Stamped.stamp(50)))


@fixture
def io_mapping() -> IoMapping:
    return IoMapping(
        Fmu(
                   str(
            Path(__file__).resolve().parent.parent.parent.parent
            / "src/simulation/models/thrusters/thruster_moduleV6.fmu"
        ),
            timedelta(seconds=0.001),
        ),
        ThrustersSensorValues,
        ThrustersSimulationOutputs,
    )

@fixture
def control() -> ThrustersControl:
    return ThrustersControl(ThrustersSetpoints(cooling_mix_setpoint=40))

@fixture
def executor(io_mapping, simulation_inputs):
    return SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=1)
    )


async def test_interfacer(executor, io_mapping, simulation_inputs, control):
    collector = PolarsCollector()
    interfacer = Interfacer(control, executor)
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


async def test_simulation(simulation_inputs, control):

    thrusters_model = SimulatorModel(
        fmu_path=str(
            Path(__file__).resolve().parent.parent.parent.parent
            / "src/simulation/models/thrusters/thruster_moduleV6.fmu"
        ),
        sensor_values_cls=ThrustersSensorValues,
        control_values_cls=ThrustersControlValues,
        simulation_outputs_cls=ThrustersSimulationOutputs,
        simulation_inputs=simulation_inputs,
        control = control)
    
    simulation = Simulator(thrusters_model)

    result = await simulation.run(20)

    assert result is not None 
    assert result['time'].len() == 20




