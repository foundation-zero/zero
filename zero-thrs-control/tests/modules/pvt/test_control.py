from datetime import datetime, timedelta

from pytest import approx
from input_output.definitions.control import Valve
from input_output.modules.pvt import PvtSensorValues
from orchestration.executor import SimulationExecutor


def test_recovery(io_mapping, control, simulation_inputs):
    control.to_recovery()
    sensor_values, simulation_outputs, _ = io_mapping.tick(
    control.control(PvtSensorValues.zero(), datetime.now()).values,
    simulation_inputs,
    datetime.now(),
    timedelta(seconds=30),
)
    assert simulation_outputs.pvt_module_return.flow.value > 0
    assert sensor_values.pvt_flow_main_fwd.flow.value + sensor_values.pvt_flow_main_aft.flow.value + sensor_values.pvt_flow_owners.flow.value == approx(simulation_outputs.pvt_module_return.flow.value, abs = 1e-5)
    assert simulation_outputs.pvt_module_supply.flow.value == approx(simulation_outputs.pvt_module_return.flow.value, abs = 1e-5)

async def test_pump_flow_recovery(io_mapping, control, simulation_inputs):
    executor = SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=6)
    )
    control.to_recovery()
    result = await executor.tick(
        control.control(PvtSensorValues.zero(), executor.time()).values,
    )

    while result.simulation_outputs.pvt_module_return.temperature.value < 68: # type: ignore
        control_values = control.control(
            result.sensor_values, executor.time()
        ).values
        control_values.pvt_mix_main_fwd.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_main_aft.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_mix_owners.setpoint.value = Valve.MIXING_A_TO_AB
        result = await executor.tick(control_values)

    for i in range(10):
        control_values = control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(control_values)

        assert result.sensor_values.pvt_flow_main_fwd.flow.value == approx(30, abs=1)
        assert result.sensor_values.pvt_flow_main_aft.flow.value == approx(30, abs=1)

        assert result.sensor_values.pvt_flow_owners.flow.value == approx(15, abs=1)
