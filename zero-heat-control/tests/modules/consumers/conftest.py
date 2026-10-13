from datetime import UTC, datetime, timedelta

from pytest import fixture

from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.consumers import (
    ConsumersAlarms,
    ConsumersControl,
    ConsumersControllerState,
    ConsumersControlMode,
    ConsumersParameters,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import Boundary
from thrs.input_output.definitions.system import AmcsControlMode, ControlMode
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import consumers_path

type ConsumersSimulation = Simulation[
    ConsumersSensorValues,
    ConsumersControlValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
]

type ConsumersRunner = SimulationTestRunner[
    ConsumersSensorValues,
    ConsumersControlValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
    ConsumersParameters,
    ConsumersControlMode,
    ConsumersControllerState,
]


@fixture
def parameters():
    return ConsumersParameters(
        dhw_enabled=True,
        dhw_flow_ratio_setpoint=0.33,
        adsorption_enabled=True,
        adsorption_flow_ratio_setpoint=0.33,
    )


@fixture
def control(parameters, simulation):
    return ConsumersControl(
        parameters, simulation.time, MachineStateLoggingServiceNoop()
    )


@fixture
def simulation_inputs():
    return ConsumersSimulationInputs(
        consumers_adsorption_supply=Boundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(42),
        ),
        consumers_pcm_supply=Boundary(
            temperature=Stamped.stamp(60), flow=Stamped.stamp(94)
        ),
        consumers_dhw_supply=Boundary(
            temperature=Stamped.stamp(40),
            flow=Stamped.stamp(29),
        ),
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
    )


@fixture
def simulation(simulation_inputs):
    with Fmu(consumers_path) as fmu:
        yield Simulation(
            ConsumersSensorValues,
            ConsumersSimulationOutputs,
            fmu,
            simulation_inputs,
            datetime.now(UTC),
            timedelta(seconds=1),
        )


@fixture
def alarms() -> ConsumersAlarms:
    return ConsumersAlarms()


@fixture
def runner(
    control: ConsumersControl,
    simulation: ConsumersSimulation,
    simulation_inputs: ConsumersSimulationInputs,
    alarms: ConsumersAlarms,
) -> ConsumersRunner:
    return SimulationTestRunner(simulation, simulation_inputs, control, alarms)
