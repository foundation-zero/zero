from datetime import datetime, timedelta
from pathlib import Path
from pytest import fixture
import pytest

from input_output.modules.pvt import (
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping
from tests.modules.helpers.simulation_inputs import simulator_input_field_setters


@fixture(
    params=list(
        simulator_input_field_setters(
            PvtSimulationInputs,
            ignore=[
                "pvt_pump_failure_switch_main_fwd",
                "pvt_pump_failure_switch_main_aft",
                "pvt_pump_failure_switch_owners",
                "pvt_module_supply" # FIXME: remove when used in simulation
            ],  # Switches don't lend themselves to absurdation
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_thrusters_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(
        str(
            Path(__file__).resolve().parent.parent.parent.parent
            / "src/simulation/models/pvt/pvt_moduleV2.fmu"
        )
    ) as fmu:
        mapping = IoMapping(
            fmu,
            PvtSensorValues,
            PvtSimulationOutputs,
        )

        with pytest.raises(Exception):
            mapping.tick(
                control.initial(datetime.now()).values,
                incorrect_simulation_inputs,
                datetime.now(),
                timedelta(seconds=1),
            )
