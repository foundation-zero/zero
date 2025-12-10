from datetime import datetime, timedelta
from pytest import fixture

from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import Boundary, FmuBoundary
from thrs.input_output.modules.consumers import (
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)


from thrs.control.modules.consumers import ConsumersControl, ConsumersParameters
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import consumers_path
from thrs.simulation.io_mapping import ThrsModelIoMapping


@fixture
def parameters():
    return ConsumersParameters(
        boosting_enabled=True,
        boosting_flow_ratio_setpoint=0.33,
        fahrenheit_enabled=True,
        fahrenheit_flow_ratio_setpoint=0.33,
    )


@fixture
def control(parameters, executor):
    return ConsumersControl(parameters, executor.time)


@fixture
def simulation_inputs():
    return ConsumersSimulationInputs(
        consumers_fahrenheit_supply=FmuBoundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(42),
            overpressure=Stamped.stamp(0.2),
        ),
        consumers_module_supply=Boundary(
            temperature=Stamped.stamp(60), flow=Stamped.stamp(94)
        ),
        consumers_boosting_supply=FmuBoundary(
            temperature=Stamped.stamp(40),
            flow=Stamped.stamp(29),
            overpressure=Stamped.stamp(0.2),
        ),
    )


@fixture
def io_mapping():
    return ThrsModelIoMapping(
        ConsumersSensorValues,
        ConsumersSimulationOutputs,
    )


@fixture
def executor(io_mapping, simulation_inputs):
    with Fmu(consumers_path) as fmu:
        yield SimulationExecutor(
            io_mapping, fmu, simulation_inputs, datetime.now(), timedelta(seconds=1)
        )
