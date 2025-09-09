from pytest import approx
from control.modules.consumers import ConsumersControl
from input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from orchestration.executor import SimulationExecutor

type ConsumersExecutor = SimulationExecutor[
    ConsumersSensorValues,
    ConsumersControlValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
]


async def test_basic(control: ConsumersControl, executor: ConsumersExecutor):
    result = await executor.tick(
        control.control(ConsumersSensorValues.zero(), executor.time()).values,
    )

    for i in range(300):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    total_flow = (
        result.sensor_values.consumers_flow_boosting.flow.value
        + result.sensor_values.consumers_flow_fahrenheit.flow.value
        + result.sensor_values.consumers_flow_bypass.flow.value
    )
    assert result.sensor_values.consumers_flow_boosting.flow.value == approx(
        total_flow * control._parameters.boosting_flow_ratio_setpoint, abs=1.0
    )
    assert result.sensor_values.consumers_flow_fahrenheit.flow.value == approx(total_flow * control._parameters.fahrenheit_flow_ratio_setpoint, abs=1.0
    )


async def test_boosting_disabled(
    control: ConsumersControl, executor: ConsumersExecutor
):
    control._parameters.boosting_enabled = False
    control._parameters.fahrenheit_flow_ratio_setpoint = 0.5
    result = await executor.tick(
        control.control(ConsumersSensorValues.zero(), executor.time()).values,
    )

    for i in range(180):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    assert result.sensor_values.consumers_flow_boosting.flow.value == approx(0, abs=0.2)
    assert result.sensor_values.consumers_flow_fahrenheit.flow.value == approx(
        result.sensor_values.consumers_flow_bypass.flow.value, abs=1.0
    )


async def test_fahrenheit_disabled(
    control: ConsumersControl, executor: ConsumersExecutor
):
    control._parameters.fahrenheit_enabled = False
    control._parameters.boosting_flow_ratio_setpoint = 0.5
    result = await executor.tick(
        control.control(ConsumersSensorValues.zero(), executor.time()).values,
    )

    for i in range(180):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    assert result.sensor_values.consumers_flow_boosting.flow.value == approx(
        result.sensor_values.consumers_flow_bypass.flow.value, abs=1.0
    )
    assert result.sensor_values.consumers_flow_fahrenheit.flow.value == approx(
        0, abs=0.2
    )


async def test_only_bypass(control: ConsumersControl, executor: ConsumersExecutor):
    control._parameters.boosting_enabled = False
    control._parameters.fahrenheit_enabled = False
    result = await executor.tick(
        control.control(ConsumersSensorValues.zero(), executor.time()).values,
    )

    for i in range(180):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    assert result.sensor_values.consumers_flow_boosting.flow.value == approx(0, abs=0.2)
    assert result.sensor_values.consumers_flow_fahrenheit.flow.value == approx(
        0, abs=0.2
    )
    assert result.sensor_values.consumers_flow_bypass.flow.value == approx(
        result.simulation_outputs.consumers_module_return.flow.value, abs=0.1
    )
