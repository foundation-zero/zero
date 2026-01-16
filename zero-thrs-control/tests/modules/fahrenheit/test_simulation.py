
from pytest import fixture
import pytest

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.input_output.modules.fahrenheit import FahrenheitSensorValues, FahrenheitSimulationInputs, FahrenheitSimulationOutputs
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping
from thrs.simulation.models.fmu_paths import fahrenheit_path
from datetime import datetime, timedelta


@fixture(
    params=list(
        simulator_input_field_setters(
            FahrenheitSimulationInputs,
            ignore=[ ]
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_thrusters_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(fahrenheit_path) as fmu:
        mapping = ThrsModelIoMapping(
            FahrenheitSensorValues,
            FahrenheitSimulationOutputs,
        )
        executor = SimulationExecutor(
            mapping,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for i in range(100):
                await executor.tick(
                    control.initial(datetime.now()).values,
                )
