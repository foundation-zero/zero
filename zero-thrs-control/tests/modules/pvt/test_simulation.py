from datetime import datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.input_output.modules.pvt import (
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping
from thrs.simulation.models.fmu_paths import pvt_path


@fixture(
    params=list(
        simulator_input_field_setters(
            PvtSimulationInputs,
            ignore=[
                "pvt_pump_failure_switch_main_fwd",
                "pvt_pump_failure_switch_main_aft",
                "pvt_pump_failure_switch_owners",
                "pvt_module_supply",
            ],  # Switches don't lend themselves to absurdation
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_thrusters_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(pvt_path) as fmu:
        mapping = ThrsModelIoMapping(
            PvtSensorValues,
            PvtSimulationOutputs,
        )
        executor = SimulationExecutor(
            mapping,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for i in range(100):
                await executor.tick(
                    control.initial(datetime.now()).values,
                )
