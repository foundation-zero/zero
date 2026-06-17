from datetime import datetime, timedelta

from pytest import fixture

from thrs.control.modules.thrusters import (
    ThrustersAlarms,
    ThrustersControl,
    ThrustersParameters,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    Pcs,
    TemperatureBoundary,
    Thruster,
)
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import thrusters_path

type ThrustersSimulation = Simulation[
    ThrustersSensorValues,
    ThrustersControlValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
]


@fixture
def simulation_inputs():
    return ThrustersSimulationInputs(
        thrusters_thruster_aft=Thruster(
            heat_flow=Stamped.stamp(9000), active=Stamped.stamp(True)
        ),
        thrusters_thruster_fwd=Thruster(
            heat_flow=Stamped.stamp(4300), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        thrusters_pcm_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
    )


@fixture
def control(simulation):
    return ThrustersControl(ThrustersParameters(), simulation.time)


@fixture
def simulation(fmu, simulation_inputs) -> ThrustersSimulation:
    return Simulation(
        ThrustersSensorValues,
        ThrustersSimulationOutputs,
        fmu,
        simulation_inputs,
        datetime.now(),
        timedelta(seconds=1),
    )


@fixture
def fmu():
    with Fmu(thrusters_path) as fmu:
        yield fmu


@fixture
def alarms() -> ThrustersAlarms:
    return ThrustersAlarms()
