from datetime import datetime, timedelta
from pytest import fixture
import pytest

from input_output.modules.pcm import (
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping
from tests.modules.helpers.simulation_inputs import simulator_input_field_setters
from simulation.models.fmu_paths import pcm_path


@fixture(
    params=list(
        simulator_input_field_setters(
            PcmSimulationInputs,
            ignore=[
                ("pcm_freshwater_supply", "flow"),
                ("pcm_producers_supply", "flow")  # Flows appear to just work, instead of break
            ]
        )
    )
)

def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_pcm_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(pcm_path) as fmu:
        mapping = IoMapping(
            fmu,
            PcmSensorValues,
            PcmSimulationOutputs,
        )

        with pytest.raises(Exception):
            for i in range(300):
                mapping.tick(
                    control.initial(datetime.now()).values,
                    incorrect_simulation_inputs,
                    datetime.now(),
                    timedelta(seconds=1),
                )
