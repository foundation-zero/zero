from typing import cast
from pytest import approx
from input_output.base import Stamped
from input_output.definitions.control import Valve
from input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from orchestration.executor import SimulationExecutor

type PvtExecutor = SimulationExecutor[
    PvtSensorValues,
    PvtControlValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
]

async def test_idle(control, executor: PvtExecutor):

    control.to_idle()
    result = await executor.tick(
        control.control(PvtSensorValues.zero(), executor.time()).values,
    )

    for i in range(30):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    assert result.simulation_outputs.pvt_module_return.flow.value == approx(0, abs =1) # type: ignore #TODO: reduce margin after fmu test (dutypoint of pump in idle mode currently set to .1)

async def test_recovery(control, executor):

    control.to_recovery()
    result = await executor.tick(
        control.control(PvtSensorValues.zero(), executor.time()).values,
    )

    for i in range(30):
        control_values = control.control(result.sensor_values, executor.time()).values
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


async def test_recovery_heat_dump(control, executor: PvtExecutor):
    control.to_recovery()
    executor._simulation_inputs.pvt_module_supply.temperature = Stamped.stamp(65)
    result = await executor.tick(
        control.control(PvtSensorValues.zero(), executor.time()).values,
    )

    for i in range(300):
        control_values = control.control(result.sensor_values, executor.time()).values
        # Pre heat PVT with hot supply water
        # Otherwise supply water is ignored, as PVTs are stuck circulating
        control_values.pvt_mix_main_fwd.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_main_aft.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_owners.setpoint.value = Valve.MIXING_A_TO_AB
        result = await executor.tick(control_values)

    for i in range(900):
        # Increasing supply temperature by 5 degrees every tick within 65 to 90 degrees
        executor._simulation_inputs.pvt_module_supply.temperature = Stamped.stamp(
            max(
                65,
                min(
                    90,
                    cast(
                        float,
                        result.simulation_outputs.pvt_module_return.temperature.value,
                    )
                    + 5,
                ),
            )
        )
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)
        # 92 allows for some overshoot from the setpoint of 85 degrees
        assert result.simulation_outputs.pvt_module_return.temperature.value < 92  # type: ignore

    assert (
        result.sensor_values.pvt_temperature_exchanger.temperature.value
        < executor._simulation_inputs.pvt_module_supply.temperature.value
    )


async def test_pump_flow_recovery(control, executor):

    control.to_recovery()
    result = await executor.tick(
        control.control(PvtSensorValues.zero(), executor.time()).values,
    )

    # owners takes longest to warm up
    while result.sensor_values.pvt_temperature_owners_return.temperature.value < 68:  # type: ignore
        control_values = control.control(result.sensor_values, executor.time()).values
        control_values.pvt_mix_main_fwd.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_main_aft.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_owners.setpoint.value = Valve.MIXING_A_TO_AB
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.pvt_flow_main_fwd.flow.value == approx(30, abs=1)
        assert result.sensor_values.pvt_flow_main_aft.flow.value == approx(30, abs=1)

        assert result.sensor_values.pvt_flow_owners.flow.value == approx(15, abs=1)


async def test_pump_flow_pump_failure(control, pump_failure_executor):
    executor = pump_failure_executor

    control.to_pump_failure()
    result = await executor.tick(
        control.control(PvtSensorValues.zero(), executor.time()).values,
    )

    # owners takes longest to warm up
    while result.sensor_values.pvt_temperature_owners_return.temperature.value < 68:  # type: ignore
        control_values = control.control(result.sensor_values, executor.time()).values
        # Simulate pump failure
        control_values.pvt_pump_main_fwd.dutypoint.value = 0
        control_values.pvt_pump_main_fwd.on.value = False
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values, executor.time()).values
        # Simulate pump failure
        control_values.pvt_pump_main_fwd.dutypoint.value = 0
        control_values.pvt_pump_main_fwd.on.value = False

        result = await executor.tick(control_values)

        assert result.sensor_values.pvt_flow_main_fwd.flow.value == approx(30, abs=5)
        assert result.sensor_values.pvt_flow_main_aft.flow.value == approx(30, abs=5)
        assert result.sensor_values.pvt_flow_owners.flow.value == approx(15, abs=2)
