from datetime import datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.input_output.modules.consumers import (
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import consumers_path


@fixture(
    params=list(
        simulator_input_field_setters(
            ConsumersSimulationInputs,
            ignore=[
                ("consumers_fahrenheit_supply", "flow"),
                ("consumers_module_supply", "flow"),
            ],  # Flows appear to just work, instead of break
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


def test_consumers_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(consumers_path) as fmu:
        simulation = Simulation(
            ConsumersSensorValues,
            ConsumersSimulationOutputs,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for i in range(300):
                simulation.tick(
                    control.initial(datetime.now()).values,
                )
