from pytest import approx
import pytest
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Valve
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor

type PvtExecutor = SimulationExecutor[
    PvtSensorValues,
    PvtControlValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
]


async def test_idle(control, executor: PvtExecutor):
    control.to_idle()
    result = await executor.tick(
        control.control(PvtSensorValues.zero()).values,
    )

    for i in range(30):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert result.simulation_outputs.pvt_module_return.flow.value == approx(0, abs=0.1)  # type: ignore


async def test_recovery(control, executor):
    control.to_recovery()
    result = await executor.tick(
        control.control(PvtSensorValues.zero()).values,
    )

    for i in range(30):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert result.simulation_outputs.pvt_module_return.flow.value > 0
    assert (
        result.sensor_values.pvt_flow_main_fwd.flow.value
        + result.sensor_values.pvt_flow_main_aft.flow.value
        + result.sensor_values.pvt_flow_owners.flow.value
        == approx(result.simulation_outputs.pvt_module_return.flow.value, abs=1e-5)
    )
    assert result.simulation_outputs.pvt_module_supply.flow.value == approx(
        result.simulation_outputs.pvt_module_return.flow.value, abs=1e-5
    )


@pytest.mark.skip("Rework test after control update")
async def test_recovery_heat_dump(
    control, executor: PvtExecutor
):  # TODO: tune heat dump controller - test fails due to overshoot
    executor._simulation_inputs.pvt_module_supply.temperature = Stamped.stamp(
        control.parameters.heat_dump_setpoint + 5
    )
    executor._simulation_inputs.pvt_seawater_supply.flow = Stamped.stamp(100)
    executor._simulation_inputs.pvt_seawater_supply.temperature = Stamped.stamp(10)

    # get initial control values
    control.to_recovery()
    control_values = control._current_values
    control_values.pvt_mix_main_fwd.setpoint.value = Valve.MIXING_A_TO_AB
    control_values.pvt_mix_main_aft.setpoint.value = Valve.MIXING_A_TO_AB
    control_values.pvt_mix_owners.setpoint.value = Valve.MIXING_A_TO_AB
    control_values.pvt_mix_exchanger.setpoint.value = Valve.MIXING_A_TO_AB

    result = await executor.tick(
        control.control(PvtSensorValues.zero()).values,
    )

    # Pre-heat PVT with hot supply water to skip time needed to warm up
    while (
        result.simulation_outputs.pvt_module_return.temperature.value
        <= executor._simulation_inputs.pvt_module_supply.temperature.value
    ):  # type: ignore
        control_values = control.control(result.sensor_values).values
        control_values.pvt_mix_main_fwd.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_main_aft.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_owners.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_exchanger.setpoint.value = Valve.MIXING_A_TO_AB
        result = await executor.tick(control_values)

    for i in range(300):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)
        assert (
            result.sensor_values.pvt_temperature_exchanger.temperature.value
            == approx(control._parameters.heat_dump_setpoint, abs=1)
        )  # type: ignore


@pytest.mark.skip("Rework test after control update")
async def test_pump_flow_recovery(control, executor):  # TODO: tune pump control..
    # get initial control values
    control.to_recovery()
    control_values = control._current_values
    control_values.pvt_mix_main_fwd.setpoint.value = Valve.MIXING_A_TO_AB
    control_values.pvt_mix_main_aft.setpoint.value = Valve.MIXING_A_TO_AB
    control_values.pvt_mix_owners.setpoint.value = Valve.MIXING_A_TO_AB
    control_values.pvt_mix_exchanger.setpoint.value = Valve.MIXING_A_TO_AB

    result = await executor.tick(
        control.control(PvtSensorValues.zero()).values,
    )

    # Pre-heat PVT with hot supply water to skip time needed to warm up
    while (
        result.simulation_outputs.pvt_module_return.temperature.value
        <= executor._simulation_inputs.pvt_module_supply.temperature.value
    ):  # type: ignore
        control_values = control.control(result.sensor_values).values
        control_values.pvt_mix_main_fwd.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_main_aft.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_owners.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_exchanger.setpoint.value = Valve.MIXING_A_TO_AB
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

        assert result.sensor_values.pvt_flow_main_fwd.flow.value == approx(
            control._parameters.main_fwd_flow_setpoint, abs=1
        )
        assert result.sensor_values.pvt_flow_main_aft.flow.value == approx(
            control._parameters.main_aft_flow_setpoint, abs=1
        )

        assert result.sensor_values.pvt_flow_owners.flow.value == approx(
            control._parameters.owners_flow_setpoint, abs=1
        )


@pytest.mark.skip("Rework test after control update")
async def test_pump_flow_pump_failure(
    control, pump_failure_executor
):  # TODO: tune pump control
    # get initial control values
    control.to_recovery()
    control_values = control._current_values
    control_values.pvt_mix_main_fwd.setpoint.value = Valve.MIXING_A_TO_AB
    control_values.pvt_mix_main_aft.setpoint.value = Valve.MIXING_A_TO_AB
    control_values.pvt_mix_owners.setpoint.value = Valve.MIXING_A_TO_AB
    control_values.pvt_mix_exchanger.setpoint.value = Valve.MIXING_A_TO_AB

    result = await pump_failure_executor.tick(
        control.control(PvtSensorValues.zero(), pump_failure_executor.time()).values,
    )

    # Pre-heat PVT with hot supply water to skip time needed to warm up
    while (
        result.simulation_outputs.pvt_module_return.temperature.value
        <= pump_failure_executor._simulation_inputs.pvt_module_supply.temperature.value
    ):  # type: ignore
        control_values = control.control(
            result.sensor_values, pump_failure_executor.time()
        ).values
        control_values.pvt_mix_main_fwd.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_main_aft.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_owners.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_exchanger.setpoint.value = Valve.MIXING_A_TO_AB
        result = await pump_failure_executor.tick(control_values)

    for i in range(60):
        control_values = control.control(
            result.sensor_values, pump_failure_executor.time()
        ).values
        # Simulate pump failure
        control_values.pvt_pump_main_fwd.dutypoint.value = 0
        control_values.pvt_pump_main_fwd.on.value = False

        result = await pump_failure_executor.tick(control_values)

        assert result.sensor_values.pvt_flow_main_fwd.flow.value > 0
        assert result.sensor_values.pvt_flow_main_aft.flow.value == approx(
            control._parameters.main_aft_flow_setpoint, abs=1
        )

        assert result.sensor_values.pvt_flow_owners.flow.value == approx(
            control._parameters.owners_flow_setpoint, abs=1
        )
