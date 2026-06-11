from datetime import datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.input_output.modules.lt2 import (
    Lt2ControlValues,
    Lt2SensorValues,
    Lt2SimulationInputs,
    Lt2SimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping
from thrs.simulation.models.fmu_paths import lt2_path


@fixture(params=list(simulator_input_field_setters(Lt2SimulationInputs)))
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_simulation_step(control, simulation):
    result = await simulation.tick(control.initial().values)

    assert isinstance(result.simulation_outputs, Lt2SimulationOutputs)


async def test_lt2_simulation_inputs(incorrect_simulation_inputs):
    with Fmu(lt2_path) as fmu:
        mapping = ThrsModelIoMapping(
            Lt2SensorValues,
            Lt2SimulationOutputs,
        )
        simulation = Simulation(
            mapping,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for i in range(300):
                await simulation.tick(
                    Lt2ControlValues.zero(),  # TODO: add actual control values
                )
