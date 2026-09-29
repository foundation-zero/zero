from datetime import UTC, datetime, timedelta

import pytest
from pytest import approx, fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import Boundary
from thrs.input_output.definitions.units import WATER_HEAT_TRANSFER_CONVERSION
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
                ("consumers_pcm_supply", "flow"),
                "mode",
            ],  # Do not throw an exception
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    request.param(simulation_inputs, -9e7)
    return simulation_inputs


def test_consumers_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(consumers_path) as fmu:
        simulation = Simulation(
            ConsumersSensorValues,
            ConsumersSimulationOutputs,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(UTC),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for _i in range(300):
                simulation.tick(
                    control.initial()[0],
                )


@pytest.mark.xfail(
    strict=True,
    reason="Consumer FMU wires the DHW supply flow to the booster source's "
    "overpressure input instead of its volume flow input",
)
def test_dhw_exchanger_balances_heat(simulation, simulation_inputs, control):
    dhw_inlet, dhw_flow = 10.0, 29.0
    simulation_inputs.consumers_dhw_supply = Boundary(
        temperature=Stamped.stamp(dhw_inlet), flow=Stamped.stamp(dhw_flow)
    )

    result = simulation.tick(control.initial()[0])
    for _i in range(600):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    dhw_outlet = result.simulation_outputs.consumers_dhw_return.temperature.value
    heat_to_dhw = dhw_flow * (dhw_outlet - dhw_inlet) * WATER_HEAT_TRANSFER_CONVERSION
    heat_from_high_temperature = (
        -result.sensor_values.consumers_dhw_exchanger.heat.value
    )

    assert heat_to_dhw == approx(heat_from_high_temperature, rel=0.1)
