from collections.abc import Generator
from datetime import datetime, timedelta

from pytest import fixture

from tests.modules.thrusters.conftest import ThrustersSimulation
from thrs.classes.machine_state_logger import (
    MachineStateLoggingService,
)
from thrs.control.modules.thrusters import ThrustersControl, ThrustersParameters
from thrs.input_output.modules.thrusters import (
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.runtime.descriptions.simulation import SIMULATION_INPUTS
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import thrusters_path


@fixture
def simulation_inputs():
    return SIMULATION_INPUTS["thrusters"]


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
def thrusters_control(simulation: ThrustersSimulation, postgres_db) -> ThrustersControl:
    return ThrustersControl(
        parameters=ThrustersParameters(),
        time_fn=simulation.time,
        state_logger=MachineStateLoggingService(postgres_db),
    )
