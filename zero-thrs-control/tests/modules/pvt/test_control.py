from pytest import approx
from input_output.definitions.control import Valve
from input_output.modules.pvt import PvtSensorValues


async def test_recovery(control, executor):

    control.to_recovery()
    result = await executor.tick(
        control.control(PvtSensorValues.zero(), executor.time()).values,
    )

    for i in range(30):
        control_values = control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(control_values)

    assert result.simulation_outputs.pvt_module_return.flow.value > 0
    assert result.sensor_values.pvt_flow_main_fwd.flow.value + result.sensor_values.pvt_flow_main_aft.flow.value + result.sensor_values.pvt_flow_owners.flow.value == approx(result.simulation_outputs.pvt_module_return.flow.value, abs = 1e-5)
    assert result.simulation_outputs.pvt_module_supply.flow.value == approx(result.simulation_outputs.pvt_module_return.flow.value, abs = 1e-5)

async def test_pump_flow_recovery(control, executor):

    control.to_recovery()
    result = await executor.tick(
        control.control(PvtSensorValues.zero(), executor.time()).values,
    )

    #owners takes longest to warm up
    while result.sensor_values.pvt_temperature_owners_return.temperature.value < 68: # type: ignore
        control_values = control.control(
            result.sensor_values, executor.time()
        ).values
        control_values.pvt_mix_main_fwd.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_main_aft.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_owners.setpoint.value = Valve.MIXING_A_TO_AB
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(control_values)

        assert result.sensor_values.pvt_flow_main_fwd.flow.value == approx(30, abs=1)
        assert result.sensor_values.pvt_flow_main_aft.flow.value == approx(30, abs=1)

        assert result.sensor_values.pvt_flow_owners.flow.value == approx(15, abs=1)
