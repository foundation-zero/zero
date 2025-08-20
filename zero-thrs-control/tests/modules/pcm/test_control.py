from pytest import approx
from control.modules.pcm import PcmControl
from input_output.definitions.control import Valve
from input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from orchestration.executor import SimulationExecutor

type PcmExecutor = SimulationExecutor[
    PcmSensorValues,
    PcmControlValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
]


async def test_idle(control: PcmControl, executor: PcmExecutor):
    result = await executor.tick(
        control.control(PcmSensorValues.zero(), executor.time()).values,
    )

    for i in range(100):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    pcm_flow = (
        result.sensor_values.pcm_flow_module_1.flow.value
        + result.sensor_values.pcm_flow_module_2.flow.value
        + result.sensor_values.pcm_flow_module_3.flow.value
        + result.sensor_values.pcm_flow_module_4.flow.value
    )
    assert control.mode == "idle"
    assert pcm_flow == approx(0.0, abs=0.1)
    assert result.simulation_inputs.get_values_at_time(
        executor.time()
    ).pcm_producers_supply.flow.value == approx(
        result.simulation_outputs.pcm_consumers_return.flow.value
    )  # type: ignore


async def test_charging(control: PcmControl, executor: PcmExecutor):
    control.to_charging()  # type: ignore
    control._current_values.pcm_switch_consumers.setpoint.value = (
        Valve.CLOSED
    )  # close consumers switch to force flow past PCM

    result = await executor.tick(
        control.control(PcmSensorValues.zero(), executor.time()).values,
    )

    for i in range(100):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    pcm_flow = (
        result.sensor_values.pcm_flow_module_1.flow.value
        + result.sensor_values.pcm_flow_module_2.flow.value
        + result.sensor_values.pcm_flow_module_3.flow.value
        + result.sensor_values.pcm_flow_module_4.flow.value
    )

    assert (
        result.sensor_values.pcm_switch_charging_supply.position_rel.value
        == result.sensor_values.pcm_switch_charging_return.position_rel.value
        == approx(1.0)
    )
    assert pcm_flow == approx(
        result.simulation_inputs.get_values_at_time(
            executor.time()
        ).pcm_producers_supply.flow.value,
        abs=.1,
    )  # type: ignore
    assert result.simulation_inputs.get_values_at_time(
        executor.time()
    ).pcm_producers_supply.flow.value == approx(
        result.simulation_outputs.pcm_producers_return.flow.value, abs=.1
    )  # type: ignore


async def test_supplying(control: PcmControl, executor: PcmExecutor):
    control.to_supplying()  # type: ignore
    result = await executor.tick(
        control.control(PcmSensorValues.zero(), executor.time()).values,
    )

    for i in range(100):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    pcm_flow = (
        result.sensor_values.pcm_flow_module_1.flow.value
        + result.sensor_values.pcm_flow_module_2.flow.value
        + result.sensor_values.pcm_flow_module_3.flow.value
        + result.sensor_values.pcm_flow_module_4.flow.value
    )

    assert (
        result.sensor_values.pcm_switch_charging_supply.position_rel.value
        == result.sensor_values.pcm_switch_charging_return.position_rel.value
        == approx(0.0, abs=0.01)
    )
    assert result.sensor_values.pcm_switch_discharging.position_rel.value == approx(1.0)
    assert result.sensor_values.pcm_pump.flow.value == approx(pcm_flow, abs=.1)
    assert result.simulation_inputs.get_values_at_time(
        executor.time()
    ).pcm_producers_supply.flow.value + pcm_flow == approx(
        result.simulation_outputs.pcm_consumers_return.flow.value, abs=.1
    )  # type: ignore
    assert result.simulation_inputs.get_values_at_time(
        executor.time()
    ).pcm_producers_supply.flow.value == approx(
        result.simulation_outputs.pcm_producers_return.flow.value, abs=.1
    )  # type: ignore


async def test_boosting(control: PcmControl, executor: PcmExecutor):
    control.to_boosting()  # type: ignore

    result = await executor.tick(
        control.control(PcmSensorValues.zero(), executor.time()).values,
    )

    for i in range(100):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    pcm_flow = (
        result.sensor_values.pcm_flow_module_1.flow.value
        + result.sensor_values.pcm_flow_module_2.flow.value
        + result.sensor_values.pcm_flow_module_3.flow.value
        + result.sensor_values.pcm_flow_module_4.flow.value
    )

    assert (
        result.simulation_inputs.get_values_at_time(
            executor.time()
        ).pcm_producers_supply.flow.value
        + result.sensor_values.pcm_pump.flow.value
        == approx(pcm_flow, abs=1)
    )  # type: ignore
    assert pcm_flow == approx(
        result.simulation_outputs.pcm_consumers_return.flow.value, abs=.1
    )
    assert result.simulation_inputs.get_values_at_time(
        executor.time()
    ).pcm_producers_supply.flow.value == approx(
        result.simulation_outputs.pcm_producers_return.flow.value, abs=.1
    )  # type: ignore
