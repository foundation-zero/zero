import pytest
from fmpy.fmi1 import FMICallException
from pydantic import ValidationError
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from tests.modules.pcm.conftest import PcmSimulation
from thrs.control.modules.pcm import PcmControl
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Valve
from thrs.input_output.definitions.simulation import Boundary
from thrs.input_output.modules.pcm import PcmSimulationInputs


@fixture
def simulation_inputs(simulation_inputs: PcmSimulationInputs) -> PcmSimulationInputs:
    return simulation_inputs.model_copy(
        update={
            "pcm_freshwater_supply": Boundary(
                temperature=Stamped.stamp(10), flow=Stamped.stamp(10)
            )
        }
    )


@fixture(
    params=list(
        simulator_input_field_setters(
            PcmSimulationInputs,
            ignore=[
                "mode",  # Not a physical quantity
                # The FMU tolerates these, even with the control running
                ("pcm_thrusters_supply", "flow"),
                ("pcm_pvt_supply", "flow"),
                ("pcm_freshwater_supply", "flow"),
            ],
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    request.param(simulation_inputs, -9e7)
    return simulation_inputs


def test_pcm_simulation_inputs(
    incorrect_simulation_inputs: PcmSimulationInputs,
    simulation: PcmSimulation,
    control: PcmControl,
):
    control_values, _ = control.initial()
    control_values.pcm_switch_charging_return.setpoint.value = Valve.OPEN
    control_values.pcm_switch_charging_supply.setpoint.value = Valve.OPEN

    with pytest.raises((ValidationError, FMICallException)):
        for _i in range(300):
            simulation.tick(control_values)
