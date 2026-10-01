from datetime import timedelta

import pytest
from fmpy.fmi1 import FMICallException
from pydantic import ValidationError
from pytest import approx, fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from tests.modules.consumers.conftest import ConsumersRunner, ConsumersSimulation
from thrs.control.modules.consumers import ConsumersControl
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import Boundary
from thrs.input_output.definitions.units import WATER_HEAT_TRANSFER_CONVERSION
from thrs.input_output.modules.consumers import ConsumersSimulationInputs


@fixture(
    params=list(
        simulator_input_field_setters(
            ConsumersSimulationInputs,
            ignore=[
                "mode",  # Not a physical quantity
                # The FMU tolerates this, even with the control running
                ("consumers_pcm_supply", "flow"),
            ],
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    request.param(simulation_inputs, -9e7)
    return simulation_inputs


def test_consumers_simulation_inputs(
    incorrect_simulation_inputs: ConsumersSimulationInputs,
    simulation: ConsumersSimulation,
    control: ConsumersControl,
):
    control_values, _ = control.initial()

    with pytest.raises((ValidationError, FMICallException)):
        for _i in range(300):
            simulation.tick(control_values)


@pytest.mark.xfail(
    strict=True,
    reason="Consumer FMU wires the DHW supply flow to the booster source's "
    "overpressure input instead of its volume flow input",
)
def test_dhw_exchanger_balances_heat(
    runner: ConsumersRunner, simulation_inputs: ConsumersSimulationInputs
):
    dhw_inlet, dhw_flow = 10.0, 29.0
    runner.update_simulation_inputs(
        simulation_inputs.model_copy(
            update={
                "consumers_dhw_supply": Boundary(
                    temperature=Stamped.stamp(dhw_inlet), flow=Stamped.stamp(dhw_flow)
                )
            }
        )
    )

    for _ in runner.ticks_for(timedelta(minutes=10)):
        pass
    sensor_values, *_ = runner.tick()

    simulation_outputs = runner.simulation_outputs
    assert simulation_outputs is not None
    dhw_outlet = simulation_outputs.consumers_dhw_return.temperature.value
    heat_to_dhw = dhw_flow * (dhw_outlet - dhw_inlet) * WATER_HEAT_TRANSFER_CONVERSION
    exchanger_heat = sensor_values.consumers_dhw_exchanger.heat.value

    assert exchanger_heat is not None
    assert heat_to_dhw == approx(-exchanger_heat, rel=0.1)
