from datetime import UTC, datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.input_output.modules.pcm import (
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import pcm_path


@fixture(
    params=list(
        simulator_input_field_setters(
            PcmSimulationInputs,
            ignore=[],  # TODO: Figure out correct variables to ignore
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    request.param(simulation_inputs, -9e7)
    return simulation_inputs


def test_pcm_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(pcm_path) as fmu:
        simulation = Simulation(
            PcmSensorValues,
            PcmSimulationOutputs,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(UTC),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for _i in range(300):
                simulation.tick(
                    control.initial(datetime.now(UTC)),
                )
