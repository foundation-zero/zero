from datetime import timedelta
from pathlib import Path
from pytest import fixture
from input_output.base import Stamped
from input_output.definitions.simulation import Boundary, HeatSource, TemperatureBoundary
from input_output.modules.thrusters import ThrustersSensorValues, ThrustersSimulationInputs, ThrustersSimulationOutputs
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

