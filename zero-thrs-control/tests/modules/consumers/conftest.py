from datetime import datetime, timedelta

from pytest import fixture

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
from thrs.simulation.io_mapping import ThrsModelIoMapping
from thrs.simulation.models.fmu_paths import consumers_path


@fixture
def parameters():
    return ConsumersParameters(
        boosting_enabled=True,
        boosting_flow_ratio_setpoint=0.33,
        fahrenheit_enabled=True,
        fahrenheit_flow_ratio_setpoint=0.33,
    )


@fixture
def control(parameters, simulation):
    return ConsumersControl(parameters, simulation.time)


@fixture
def simulation_inputs():
    return ConsumersSimulationInputs(
        consumers_fahrenheit_supply=Boundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(42),
        ),
        consumers_module_supply=Boundary(
            temperature=Stamped.stamp(60), flow=Stamped.stamp(94)
        ),
        consumers_boosting_supply=Boundary(
            temperature=Stamped.stamp(40),
            flow=Stamped.stamp(29),
        ),
    )


@fixture
def io_mapping():
    return ThrsModelIoMapping(
        ConsumersSensorValues,
        ConsumersSimulationOutputs,
    )


@fixture
def simulation(io_mapping, simulation_inputs):
    with Fmu(consumers_path) as fmu:
        yield Simulation(
            io_mapping, fmu, simulation_inputs, datetime.now(), timedelta(seconds=1)
        )
