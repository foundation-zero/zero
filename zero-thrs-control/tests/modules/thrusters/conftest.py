from datetime import datetime, timedelta
from pytest import fixture
from control.modules.thrusters import ThrustersAlarms, ThrustersControl, ThrustersParameters
from input_output.base import Stamped
from input_output.definitions.simulation import (
    Boundary,
    Pcs,
    TemperatureBoundary,
    Thruster,
)
from input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from orchestration.executor import SimulationExecutor
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping
from simulation.models.fmu_paths import thrusters_path

type ThrustersSimulationExecutor = SimulationExecutor[ThrustersSensorValues, ThrustersControlValues, ThrustersSimulationInputs, ThrustersSimulationOutputs]



@fixture
def simulation_inputs():
    return ThrustersSimulationInputs(
        thrusters_aft=Thruster(
            heat_flow=Stamped.stamp(9000), active=Stamped.stamp(True)
        ),
        thrusters_fwd=Thruster(
            heat_flow=Stamped.stamp(4300), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        thrusters_module_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
        thrusters_pcs=Pcs(mode=Stamped.stamp("propulsion")),
    )


@fixture
def io_mapping():
    with Fmu(thrusters_path) as fmu:
        yield IoMapping(
            fmu,
            ThrustersSensorValues,
            ThrustersSimulationOutputs,
        )


@fixture
def control():
    return ThrustersControl(ThrustersParameters())


@fixture
def executor(io_mapping, simulation_inputs) -> ThrustersSimulationExecutor:
    return SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=1)
    )

@fixture
def alarms() -> ThrustersAlarms:
    return ThrustersAlarms()
