from datetime import datetime, timedelta
from pytest import fixture
import pytest

from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
)
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.simulation.models.fmu_paths import high_temperature_path


@fixture(
    params=list(
        simulator_input_field_setters(
            HighTemperatureSimulationInputs,
            ignore=[
                (
                    "consumers_fahrenheit_supply",
                    "flow",
                ),  # Flows appear to just work, instead of break
                ("pvt_pump_failure_switch_main_aft", "position_rel"),
                ("pvt_pump_failure_switch_main_fwd", "position_rel"),
                (
                    "pvt_pump_failure_switch_owners",
                    "position_rel",
                ),  # TODO: figure out why this takes such a long time. Could be related to flow control.
            ],
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_high_temperature_simulation_inputs(
    incorrect_simulation_inputs, control, io_mapping
):
    with Fmu(high_temperature_path) as fmu:
        mapping = io_mapping
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
