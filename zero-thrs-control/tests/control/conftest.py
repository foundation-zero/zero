from datetime import datetime, timedelta
from typing import Generator

from pytest import fixture

from tests.modules.thrusters.conftest import ThrustersSimulation
from thrs.classes.machine_state_logger import (
    MachineStateLoggingService,
)
from thrs.control.modules.thrusters import ThrustersControl, ThrustersParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    Pcs,
    TemperatureBoundary,
    Thruster,
)
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.thrusters import (
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import thrusters_path


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
def simulation(
    simulation_inputs: ThrustersSimulationInputs,
) -> Generator[ThrustersSimulation, None, None]:
    with Fmu(thrusters_path) as fmu:
        yield Simulation(
            ThrustersSensorValues,
            ThrustersSimulationOutputs,
            fmu,
            simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )


@fixture
def thrusters_control(simulation: ThrustersSimulation) -> ThrustersControl:
    return ThrustersControl(
        parameters=ThrustersParameters(),
        time_fn=simulation.time,
        state_logger=MachineStateLoggingService(),
    )
