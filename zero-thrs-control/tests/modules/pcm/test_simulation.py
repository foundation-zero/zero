from datetime import datetime, timedelta
from pytest import fixture
import pytest

from thrs.input_output.modules.pcm import (
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping
from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.simulation.models.fmu_paths import pcm_path


@fixture(
    params=list(
        simulator_input_field_setters(
            PcmSimulationInputs,
            ignore=[
                (
                    "pcm_producers_supply",
                    "flow",
                )  # Appears to just work, instead of break
            ],
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_pcm_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(pcm_path) as fmu:
        mapping = ThrsModelIoMapping(
            PcmSensorValues,
            PcmSimulationOutputs,
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
                    control.initial(datetime.now()).values,
                )
