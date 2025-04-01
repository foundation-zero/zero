from datetime import datetime, timedelta

from pytest import approx

from input_output.base import Stamped
from input_output.definitions.control import Valve
from input_output.modules.thrusters import ThrustersSensorValues
from orchestration.executor import SimulationExecutor


def test_cooling(io_mapping, thrusters_control, simulation_inputs):
    thrusters_control.to_cooling()
    sensor_values, simulation_outputs, _ = io_mapping.tick(
        thrusters_control.control(ThrustersSensorValues.zero(), datetime.now()).values,
        simulation_inputs,
        datetime.now(),
        timedelta(seconds=60),
    )

    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_aft_return.temperature.value
    )
    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_fwd_return.temperature.value
    )

    assert sensor_values.thrusters_flow_fwd.flow.value > 1
    assert sensor_values.thrusters_flow_aft.flow.value > 1
    assert sensor_values.thrusters_flow_recovery_fwd.flow.value == approx(0, abs=1e-2)
    assert sensor_values.thrusters_flow_recovery_aft.flow.value == approx(0, abs=1e-2)
    assert simulation_outputs.thrusters_module_supply.flow.value == approx(0, abs=1e-2)
    assert simulation_outputs.thrusters_module_return.flow.value == approx(0, abs=1e-2)
    assert (
        simulation_inputs.thrusters_seawater_supply.temperature.value
        < simulation_outputs.thrusters_seawater_return.temperature.value
    )


def test_recovery(io_mapping, thrusters_control, simulation_inputs):
    thrusters_control.to_recovery()
    sensor_values, simulation_outputs, _ = io_mapping.tick(
        thrusters_control.control(ThrustersSensorValues.zero(), datetime.now()).values,
        simulation_inputs,
        datetime.now(),
        timedelta(seconds=240),
    )

    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_aft_return.temperature.value
    )
    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_fwd_return.temperature.value
    )

    assert simulation_outputs.thrusters_module_return.flow.value == approx(
        simulation_outputs.thrusters_module_supply.flow.value, abs=1e-2
    )

    assert sensor_values.thrusters_flow_recovery_fwd.flow.value + sensor_values.thrusters_flow_recovery_aft.flow.value == approx(simulation_outputs.thrusters_module_return.flow.value, abs=1e-2)
    
    
    assert (
        simulation_outputs.thrusters_module_return.temperature.value
        > simulation_inputs.thrusters_module_supply.temperature.value
    )


async def test_recovery_mixing_cold(io_mapping, thrusters_control, simulation_inputs):
    simulation_inputs.thrusters_module_supply.temperature = Stamped.stamp(20)
    executor = SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=60)
    )
    thrusters_control.to_recovery()
    result = await executor.tick(
        thrusters_control.control(ThrustersSensorValues.zero(), datetime.now()).values,
    )

    # stabilise
    for i in range(2):
        control_values = thrusters_control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(control_values)

    for i in range(40):
        control_values = thrusters_control.control(
            result.sensor_values, datetime.now()
        ).values
        result = await executor.tick(
            control_values,
        )

        if result.sensor_values.thrusters_temperature_aft_return.temperature.value < 50:
            assert control_values.thrusters_mix_aft.setpoint.value == approx(
                Valve.MIXING_B_TO_AB, abs=1e-2
            )

        if result.sensor_values.thrusters_temperature_fwd_return.temperature.value < 50:
            assert control_values.thrusters_mix_fwd.setpoint.value == approx(
                Valve.MIXING_B_TO_AB, abs=1e-2
            )

    assert result.sensor_values.thrusters_temperature_aft_return.temperature.value > 45
    assert result.sensor_values.thrusters_temperature_fwd_return.temperature.value > 45


async def test_recovery_mixing_hot(io_mapping, thrusters_control, simulation_inputs):
    simulation_inputs.thrusters_module_supply.temperature = Stamped.stamp(20)
    executor = SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=60)
    )
    thrusters_control.to_recovery()
    result = await executor.tick(
        thrusters_control.control(ThrustersSensorValues.zero(), datetime.now()).values
    )

    # stabilise
    for i in range(2):
        control_values = thrusters_control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(control_values)

    for i in range(40):
        simulation_inputs.thrusters_module_supply.temperature = Stamped.stamp(
            result.sensor_values.thrusters_temperature_fwd_return.temperature.value
        )
        control_values = thrusters_control.control(
            result.sensor_values, datetime.now()
        ).values
        result = await executor.tick(
            control_values,
        )

        if result.sensor_values.thrusters_temperature_aft_return.temperature.value > 70:
            assert control_values.thrusters_mix_aft.setpoint.value == approx(
                Valve.MIXING_A_TO_AB, abs=1e-2
            )

        if result.sensor_values.thrusters_temperature_fwd_return.temperature.value > 70:
            assert control_values.thrusters_mix_fwd.setpoint.value == approx(
                Valve.MIXING_A_TO_AB, abs=1e-2
            )

    assert (
        result.sensor_values.thrusters_temperature_aft_return.temperature.value
        == approx(60, abs=5)
    )
    assert (
        result.sensor_values.thrusters_temperature_fwd_return.temperature.value
        == approx(60, abs=5)
    )


async def test_heat_dump_with_cold_sea(
    io_mapping, thrusters_control, simulation_inputs
):
    simulation_inputs.thrusters_seawater_supply.temperature = Stamped.stamp(15)
    executor = SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=60)
    )
    thrusters_control.to_recovery()
    result = await executor.tick(
        thrusters_control.control(ThrustersSensorValues.zero(), datetime.now()).values,
    )

    # stabilise
    for i in range(2):
        control_values = thrusters_control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(control_values)

    for i in range(40):
        control_values = thrusters_control.control(
            result.sensor_values, datetime.now()
        ).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_temperature_supply.temperature.value > 35


async def test_heat_dump_with_hot_sea(io_mapping, thrusters_control, simulation_inputs):
    simulation_inputs.thrusters_seawater_supply.temperature = Stamped.stamp(45)
    executor = SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=60)
    )
    thrusters_control.to_recovery()
    result = await executor.tick(
        thrusters_control.control(ThrustersSensorValues.zero(), datetime.now()).values,
    )

    # stabilise
    for i in range(2):
        control_values = thrusters_control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(control_values)

    for i in range(40):
        control_values = thrusters_control.control(
            result.sensor_values, datetime.now()
        ).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_temperature_supply.temperature.value < 65
