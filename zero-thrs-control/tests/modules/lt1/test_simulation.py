from datetime import datetime, timedelta

from pytest import fixture
import pytest

from thrs.input_output.modules.lt1 import (
    Lt1ControlValues,
    Lt1SensorValues,
    Lt1SimulationInputs,
    Lt1SimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping
from thrs.simulation.models.fmu_paths import lt1_path
from tests.helpers.simulation_inputs import simulator_input_field_setters


@fixture(params=list(simulator_input_field_setters(Lt1SimulationInputs)))
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_lt1_simulation_inputs(incorrect_simulation_inputs):
    with Fmu(lt1_path) as fmu:
        mapping = ThrsModelIoMapping(
            Lt1SensorValues,
            Lt1SimulationOutputs,
        )
        executor = SimulationExecutor(
            mapping,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for i in range(300):
                await executor.tick(
                    Lt1ControlValues.zero(),  # TODO: add actual control values
                )
