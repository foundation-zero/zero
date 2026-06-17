from datetime import datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.input_output.modules.adsorption import (
    AdsorptionSensorValues,
    AdsorptionSimulationInputs,
    AdsorptionSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import adsorption_path


@fixture(
    params=list(simulator_input_field_setters(AdsorptionSimulationInputs, ignore=[]))
)
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_thrusters_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(adsorption_path) as fmu:
        simulation = Simulation(
            AdsorptionSensorValues,
            AdsorptionSimulationOutputs,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for i in range(100):
                await simulation.tick(
                    control.initial(datetime.now()).values,
                )
