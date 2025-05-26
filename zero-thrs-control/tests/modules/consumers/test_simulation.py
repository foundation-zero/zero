from datetime import datetime, timedelta
from pytest import fixture
import pytest

from input_output.modules.consumers import (
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping
from simulation.models.fmu_paths import consumers_path
from tests.modules.helpers.simulation_inputs import simulator_input_field_setters


@fixture(
    params=list(
        simulator_input_field_setters(
            ConsumersSimulationInputs,
            ignore=[
                ("consumers_fahrenheit_supply", "flow"),
                ("consumers_module_supply", "flow"),
            ], # Flows appear to just work, instead of break
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_thrusters_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(consumers_path) as fmu:
        mapping = IoMapping(
            fmu,
            ConsumersSensorValues,
            ConsumersSimulationOutputs,
        )

        with pytest.raises(Exception):
            for i in range(300):
                mapping.tick(
                    control.initial(datetime.now()).values,
                    incorrect_simulation_inputs,
                    datetime.now(),
                    timedelta(seconds=1),
                )
