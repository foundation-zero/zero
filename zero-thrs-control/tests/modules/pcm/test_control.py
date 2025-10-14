from pytest import approx
import pytest
from thrs.control.modules.pcm import PcmControl
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor

type PcmExecutor = SimulationExecutor[
    PcmSensorValues,
    PcmControlValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
]


async def test_idle(control: PcmControl, executor: PcmExecutor):
    result = await executor.tick(
        control.control(PcmSensorValues.zero()).values,
    )

    for i in range(100):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    pcm_flow = (
        result.sensor_values.pcm_flow_module_1.flow.value
        + result.sensor_values.pcm_flow_module_2.flow.value
        + result.sensor_values.pcm_flow_module_3.flow.value
        + result.sensor_values.pcm_flow_module_4.flow.value
    )
    assert control.mode == "idle"
    assert pcm_flow == approx(0.0, abs=0.1)
    assert result.simulation_inputs.pcm_producers_supply.flow.value == approx(
        result.simulation_outputs.pcm_consumers_return.flow.value, abs=0.01
    )  # type: ignore


async def test_charging(control: PcmControl, executor: PcmExecutor):
    result = await executor.tick(
        control.control(PcmSensorValues.zero()).values,
    )

    control.to_charging(result.sensor_values)  # type: ignore

    for i in range(200):
        control_values = control.control(result.sensor_values).values

        control_values.pcm_switch_consumers.setpoint.value = 0.4  # close consumers switch partly to force flow past PCM #TODO: implement realistic pressure drop on consumers
        result = await executor.tick(control_values)

    assert (
        result.sensor_values.pcm_switch_charging_supply.position_rel.value
        == result.sensor_values.pcm_switch_charging_return.position_rel.value
        == approx(1.0)
    )

    assert result.simulation_inputs.pcm_producers_supply.flow.value == approx(
        result.simulation_outputs.pcm_producers_return.flow.value, abs=0.1
    )  # type: ignore

    assert result.sensor_values.pcm_flow_module_1.flow.value == approx(
        control.parameters.pcm_charge_flow, abs=0.5
    )
    assert result.sensor_values.pcm_flow_module_2.flow.value == approx(
        control.parameters.pcm_charge_flow, abs=0.5
    )
    assert result.sensor_values.pcm_flow_module_3.flow.value == approx(
        control.parameters.pcm_charge_flow, abs=0.5
    )
    assert result.sensor_values.pcm_flow_module_4.flow.value == approx(
        control.parameters.pcm_charge_flow, abs=0.5
    )

    for i in range(100):
        result.sensor_values.pcm_temperature_module_1_out.temperature.value = (
            result.sensor_values.pcm_temperature_producers_return.temperature.value
        )
        result.sensor_values.pcm_temperature_module_2_out.temperature.value = (
            result.sensor_values.pcm_temperature_producers_return.temperature.value
        )
        control_values = control.control(result.sensor_values).values
        control_values.pcm_switch_consumers.setpoint.value = 0.4  # close consumers switch partly to force flow past PCM #TODO: implement realistic pressure drop on consumers
        result = await executor.tick(control_values)

    assert result.sensor_values.pcm_flow_module_1.flow.value == approx(0, abs=0.1)

    assert result.sensor_values.pcm_flow_module_2.flow.value == approx(0, abs=0.1)

    assert result.sensor_values.pcm_flow_module_3.flow.value == approx(
        control.parameters.pcm_charge_flow, abs=0.5
    )
    assert result.sensor_values.pcm_flow_module_4.flow.value == approx(
        control.parameters.pcm_charge_flow, abs=0.5
    )


async def test_supplying(control: PcmControl, executor: PcmExecutor):
    result = await executor.tick(
        control.control(PcmSensorValues.zero()).values,
    )

    control.to_supplying(result.sensor_values)  # type: ignore

    for i in range(100):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert (
        result.sensor_values.pcm_switch_charging_supply.position_rel.value
        == result.sensor_values.pcm_switch_charging_return.position_rel.value
        == approx(0.0, abs=0.01)
    )

    pcm_flow = (
        result.sensor_values.pcm_flow_module_1.flow.value
        + result.sensor_values.pcm_flow_module_2.flow.value
        + result.sensor_values.pcm_flow_module_3.flow.value
        + result.sensor_values.pcm_flow_module_4.flow.value
    )

    assert result.sensor_values.pcm_switch_discharging.position_rel.value == approx(1.0)
    assert result.sensor_values.pcm_pump.flow.value == approx(pcm_flow, abs=0.1)
    assert (
        result.simulation_inputs.pcm_producers_supply.flow.value + pcm_flow
        == approx(result.simulation_outputs.pcm_consumers_return.flow.value, abs=0.1)
    )  # type: ignore
    assert result.simulation_inputs.pcm_producers_supply.flow.value == approx(
        result.simulation_outputs.pcm_producers_return.flow.value, abs=0.1
    )  # type: ignore

    assert pcm_flow == approx(4 * control.parameters.pcm_charge_flow, abs=0.5)

    for i in range(100):
        result.sensor_values.pcm_module_1.charged.value = False
        result.sensor_values.pcm_module_2.charged.value = False
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    pcm_flow = (
        result.sensor_values.pcm_flow_module_1.flow.value
        + result.sensor_values.pcm_flow_module_2.flow.value
        + result.sensor_values.pcm_flow_module_3.flow.value
        + result.sensor_values.pcm_flow_module_4.flow.value
    )

    assert result.sensor_values.pcm_flow_module_1.flow.value == approx(0, abs=0.01)
    assert result.sensor_values.pcm_flow_module_2.flow.value == approx(0, abs=0.01)
    assert pcm_flow == approx(2 * control.parameters.pcm_charge_flow, abs=0.5)

    for i in range(100):
        result.sensor_values.pcm_module_1.charged.value = False
        result.sensor_values.pcm_module_2.charged.value = False
        result.sensor_values.pcm_module_3.charged.value = False
        result.sensor_values.pcm_module_4.charged.value = False
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    pcm_flow = (
        result.sensor_values.pcm_flow_module_1.flow.value
        + result.sensor_values.pcm_flow_module_2.flow.value
        + result.sensor_values.pcm_flow_module_3.flow.value
        + result.sensor_values.pcm_flow_module_4.flow.value
    )

    assert result.sensor_values.pcm_flow_module_1.flow.value == approx(0, abs=0.01)
    assert result.sensor_values.pcm_flow_module_2.flow.value == approx(0, abs=0.01)
    assert result.sensor_values.pcm_flow_module_3.flow.value == approx(0, abs=0.01)
    assert result.sensor_values.pcm_flow_module_4.flow.value == approx(0, abs=0.01)
    assert pcm_flow == approx(0, abs=0.01)


@pytest.mark.skip("Boosting not implemented for now")
async def test_boosting(control: PcmControl, executor: PcmExecutor):
    control.to_boosting()  # type: ignore

    result = await executor.tick(
        control.control(PcmSensorValues.zero()).values,
    )

    for i in range(100):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    pcm_flow = (
        result.sensor_values.pcm_flow_module_1.flow.value
        + result.sensor_values.pcm_flow_module_2.flow.value
        + result.sensor_values.pcm_flow_module_3.flow.value
        + result.sensor_values.pcm_flow_module_4.flow.value
    )

    assert (
        result.simulation_inputs.pcm_producers_supply.flow.value
        + result.sensor_values.pcm_pump.flow.value
        == approx(pcm_flow, abs=1)
    )  # type: ignore
    assert pcm_flow == approx(
        result.simulation_outputs.pcm_consumers_return.flow.value, abs=0.1
    )
    assert result.simulation_inputs.pcm_producers_supply.flow.value == approx(
        result.simulation_outputs.pcm_producers_return.flow.value, abs=0.1
    )  # type: ignore
