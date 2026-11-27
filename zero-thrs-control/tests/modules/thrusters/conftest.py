from datetime import UTC, datetime, timedelta

from pytest import fixture

from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.control.modules.thrusters.control import ThrustersAlarms, ThrustersControl
from thrs.control.modules.thrusters.io import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.control.modules.thrusters.state import (
    ThrustersControllerState,
    ThrustersControlMode,
    ThrustersParameters,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    Pcs,
    TemperatureBoundary,
    Thruster,
)
from thrs.input_output.definitions.system import AmcsMode, AmcsModeStatus
from thrs.input_output.definitions.units import PcsMode
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import thrusters_path

type ThrustersSimulation = Simulation[
    ThrustersSensorValues,
    ThrustersControlValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
]

type ThrustersRunner = SimulationTestRunner[
    ThrustersSensorValues,
    ThrustersControlValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
    ThrustersParameters,
    ThrustersControlMode,
    ThrustersControllerState,
]


@fixture
def simulation_inputs():
    return ThrustersSimulationInputs(
        thrusters_thruster_aft=Thruster(heat_flow=Stamped.stamp(9000)),
        thrusters_thruster_fwd=Thruster(heat_flow=Stamped.stamp(4300)),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        thrusters_pcm_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
        mode=AmcsModeStatus(mode=Stamped.stamp(AmcsMode.EXTERNAL)),
    )


@fixture
def control(simulation, postgres_db):
    return ThrustersControl(ThrustersParameters(), simulation.time)


@fixture
def simulation(fmu, simulation_inputs) -> ThrustersSimulation:
    return Simulation(
        ThrustersSensorValues,
        ThrustersSimulationOutputs,
        fmu,
        simulation_inputs,
        datetime.now(UTC),
        timedelta(seconds=1),
    )


@fixture
def fmu():
    with Fmu(thrusters_path) as fmu:
        yield fmu


@fixture
def alarms() -> ThrustersAlarms:
    return ThrustersAlarms()


@fixture
def runner(
    control: ThrustersControl,
    simulation: ThrustersSimulation,
    simulation_inputs: ThrustersSimulationInputs,
    alarms: ThrustersAlarms,
) -> ThrustersRunner:
    return SimulationTestRunner(simulation, simulation_inputs, control, alarms)
