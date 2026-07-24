from datetime import datetime, timedelta

from pytest import fixture

from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.consumers import ConsumersControl, ConsumersParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import Boundary
from thrs.input_output.modules.consumers import (
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import consumers_path


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
    )


@fixture
def simulation(simulation_inputs):
    with Fmu(consumers_path) as fmu:
        yield Simulation(
            ConsumersSensorValues,
            ConsumersSimulationOutputs,
            fmu,
            simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )
