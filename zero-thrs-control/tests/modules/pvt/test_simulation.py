import pytest
from fmpy.fmi1 import FMICallException
from pydantic import ValidationError
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from tests.modules.pvt.conftest import PvtSimulation
from thrs.control.modules.pvt import PvtControl
from thrs.input_output.definitions.control import Valve
from thrs.input_output.modules.pvt import PvtSimulationInputs


@fixture(
    params=list(
        simulator_input_field_setters(
            PvtSimulationInputs,
            ignore=[
                "pvt_pcm_supply",  # Switches don't lend themselves to absurdation
                "mode",  # Not a physical quantity
            ],
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    request.param(simulation_inputs, -9e7)
    return simulation_inputs


def test_pvt_simulation_inputs(
    incorrect_simulation_inputs: PvtSimulationInputs,
    simulation: PvtSimulation,
    control: PvtControl,
):
    control_values, _ = control.initial()
    for pump, mix in [
        (control_values.pvt_pump_main_aft, control_values.pvt_mix_main_aft),
        (control_values.pvt_pump_main_fwd, control_values.pvt_mix_main_fwd),
        (control_values.pvt_pump_owners, control_values.pvt_mix_owners),
    ]:
        pump.on.value = True
        pump.dutypoint.value = 1
        mix.setpoint.value = Valve.MIXING_A_TO_AB

    with pytest.raises((ValidationError, FMICallException)):
        for _i in range(100):
            simulation.tick(control_values)
