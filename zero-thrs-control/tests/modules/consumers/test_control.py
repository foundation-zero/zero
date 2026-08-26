from pytest import approx

from thrs.control.modules.consumers import ConsumersControl
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation

type ConsumersSimulation = Simulation[
    ConsumersSensorValues,
    ConsumersControlValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
]


def test_basic(control: ConsumersControl, simulation: ConsumersSimulation):
    result = simulation.tick(
        control.control(ConsumersSensorValues.zero())[0],
    )

    for _i in range(180):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    total_flow = (
        result.sensor_values.consumers_flow_dhw.flow.value
        + result.sensor_values.consumers_flow_adsorption.flow.value
        + result.sensor_values.consumers_flow_bypass.flow.value
    )
    assert result.sensor_values.consumers_flow_dhw.flow.value == approx(
        total_flow * control.parameters.dhw_flow_ratio_setpoint, abs=1.0
    )
    assert result.sensor_values.consumers_flow_adsorption.flow.value == approx(
        total_flow * control.parameters.adsorption_flow_ratio_setpoint, abs=1.0
    )


async def test_dhw_disabled(control: ConsumersControl, simulation: ConsumersSimulation):
    control.parameters.dhw_enabled = False
    control.parameters.adsorption_flow_ratio_setpoint = 0.5
    result = simulation.tick(
        control.control(ConsumersSensorValues.zero())[0],
    )

    for _i in range(180):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert result.sensor_values.consumers_flow_dhw.flow.value == approx(0, abs=0.1)
    assert result.sensor_values.consumers_flow_adsorption.flow.value == approx(
        result.sensor_values.consumers_flow_bypass.flow.value, abs=1.0
    )


def test_adsorption_disabled(
    control: ConsumersControl, simulation: ConsumersSimulation
):
    control.parameters.adsorption_enabled = False
    control.parameters.dhw_flow_ratio_setpoint = 0.5
    result = simulation.tick(
        control.control(ConsumersSensorValues.zero())[0],
    )

    for _i in range(180):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert result.sensor_values.consumers_flow_dhw.flow.value == approx(
        result.sensor_values.consumers_flow_bypass.flow.value, abs=1.0
    )
    assert result.sensor_values.consumers_flow_adsorption.flow.value == approx(
        0, abs=0.2
    )


def test_only_bypass(control: ConsumersControl, simulation: ConsumersSimulation):
    control.parameters.dhw_enabled = False
    control.parameters.adsorption_enabled = False
    result = simulation.tick(
        control.control(ConsumersSensorValues.zero())[0],
    )

    for _i in range(180):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert result.sensor_values.consumers_flow_dhw.flow.value == approx(0, abs=0.2)
    assert result.sensor_values.consumers_flow_adsorption.flow.value == approx(
        0, abs=0.2
    )
    assert result.sensor_values.consumers_flow_bypass.flow.value == approx(
        result.simulation_outputs.consumers_pcm_return.flow.value, abs=0.1
    )
