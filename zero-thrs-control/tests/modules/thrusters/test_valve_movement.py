from datetime import datetime, timedelta

from pytest import approx

from orchestration.executor import SimulationExecutor


async def test_valve_movement(io_mapping, control, simulation_inputs):

    executor = SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=45)
    )

    control_values = control.initial(executor.time()).values
    control_values.thrusters_shutoff_recovery.setpoint.value = 0
    result = await executor.tick(
        control_values)

    assert control_values.thrusters_shutoff_recovery.setpoint.value == 0
    assert result.sensor_values.thrusters_shutoff_recovery.position_rel.value == approx(0.5, abs = 0.01)


    result = await executor.tick(control_values)

    assert control_values.thrusters_shutoff_recovery.setpoint.value == 0
    assert result.sensor_values.thrusters_shutoff_recovery.position_rel.value == approx(0, abs = 0.01)

