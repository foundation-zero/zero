from datetime import UTC, datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.input_output.modules.pvt import (
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import pvt_path


@fixture(
    params=list(
        simulator_input_field_setters(
            PvtSimulationInputs,
            ignore=[
                "pvt_pcm_supply",
            ],  # Switches don't lend themselves to absurdation
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    request.param(simulation_inputs, -9e7)
    return simulation_inputs


def test_pvt_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(pvt_path) as fmu:
        simulation = Simulation(
            PvtSensorValues,
            PvtSimulationOutputs,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(UTC),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for _i in range(100):
                simulation.tick(
                    control.initial(datetime.now(UTC)),
                )
