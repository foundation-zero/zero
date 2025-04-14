
from pytest import approx
import pytest

from input_output.base import Stamped
from input_output.definitions.control import Valve


async def test_cooling(control, executor):
    control.to_cooling()
    control_values = control.initial(executor.time()).values

    result = await executor.tick(control_values)

    for i in range(100):
        control_values = control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(control_values)

    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_aft_return.temperature.value
    )
    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_fwd_return.temperature.value
    )

    assert result.sensor_values.thrusters_flow_recovery_fwd.flow.value == approx(0, abs=1e-2)
    assert result.sensor_values.thrusters_flow_recovery_aft.flow.value == approx(0, abs=1e-2)
    assert result.simulation_outputs.thrusters_module_supply.flow.value == approx(0, abs=1e-2)
    assert result.simulation_outputs.thrusters_module_return.flow.value == approx(0, abs=1e-2)
    assert (
        result.simulation_inputs.thrusters_seawater_supply.temperature.value
        < result.simulation_outputs.thrusters_seawater_return.temperature.value
    )


async def test_recovery(control, executor):
    control.to_recovery()

    control_values = control.initial(executor.time()).values
    result = await executor.tick(control_values)

    for i in range(100):
        control_values = control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(control_values)

    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_aft_return.temperature.value
    )
    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_fwd_return.temperature.value
    )

    assert result.simulation_outputs.thrusters_module_return.flow.value == approx(
        result.simulation_outputs.thrusters_module_supply.flow.value, abs=1e-2
    )

    assert (
        result.sensor_values.thrusters_flow_recovery_fwd.flow.value
        + result.sensor_values.thrusters_flow_recovery_aft.flow.value
        == approx(result.simulation_outputs.thrusters_module_return.flow.value, abs=1e-2)
    )

    assert (
        result.simulation_outputs.thrusters_module_return.temperature.value
        > result.simulation_inputs.thrusters_module_supply.temperature.value
    )


async def test_recovery_mixing_cold(control, executor):
    executor._boundaries.thrusters_module_supply.temperature = Stamped.stamp(20)

    control.to_recovery()

    result = await executor.tick(
        control.initial(executor.time()).values,
    )

    # stabilise
    for i in range(100):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        if result.sensor_values.thrusters_temperature_aft_return.temperature.value < 50:
            assert control_values.thrusters_mix_aft.setpoint.value == approx(
                Valve.MIXING_B_TO_AB, abs=1e-2
            )

        if result.sensor_values.thrusters_temperature_fwd_return.temperature.value < 50:
            assert control_values.thrusters_mix_fwd.setpoint.value == approx(
                Valve.MIXING_B_TO_AB, abs=1e-2
            )

    for i in range(40):
        control_values = control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(
            control_values,
        )

        assert result.sensor_values.thrusters_temperature_aft_return.temperature.value > 45
        assert result.sensor_values.thrusters_temperature_fwd_return.temperature.value > 45

#@pytest.mark.skip(reason="Need to fix bug re setting module supply temperature")
async def test_recovery_mixing_hot(control, executor):
    executor._boundaries.thrusters_module_supply.temperature = Stamped.stamp(55)

    control.to_recovery()

    result = await executor.tick(
        control.initial(executor.time()).values,
    )

    for i in range(90):
        control_values = control.control(
            result.sensor_values, executor.time()
        ).values

        control_values.thrusters_mix_aft.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.thrusters_mix_fwd.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.thrusters_pump_1.dutypoint.value = 0

        result = await executor.tick(control_values)

    # stabilise
    for i in range(80):

        control_values = control.control(
            result.sensor_values, executor.time()
        ).values

        control_values.thrusters_mix_aft.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.thrusters_mix_fwd.setpoint.value = Valve.MIXING_A_TO_AB

        result = await executor.tick(control_values)

        if result.sensor_values.thrusters_temperature_aft_return.temperature.value > 65:
            assert control_values.thrusters_mix_aft.setpoint.value == approx(
                Valve.MIXING_A_TO_AB, abs=1e-2
            )

        if result.sensor_values.thrusters_temperature_fwd_return.temperature.value > 65:
            assert control_values.thrusters_mix_fwd.setpoint.value == approx(
                Valve.MIXING_A_TO_AB, abs=1e-2
            )

        if result.sensor_values.thrusters_temperature_aft_return.temperature.value < 55:
            assert control_values.thrusters_mix_aft.setpoint.value == approx(
                Valve.MIXING_B_TO_AB, abs=1e-2
            )

        if result.sensor_values.thrusters_temperature_fwd_return.temperature.value < 55:
            assert control_values.thrusters_mix_fwd.setpoint.value == approx(
                Valve.MIXING_B_TO_AB, abs=1e-2
            )

    for i in range(40):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(
            control_values,
        )

        assert (
            result.sensor_values.thrusters_temperature_aft_mix.temperature.value
            == approx(60, abs=2)
        )
        assert (
            result.sensor_values.thrusters_temperature_fwd_mix.temperature.value
            == approx(60, abs=2)
        )


async def test_heat_dump_with_cold_sea(
    control, executor
):
    executor._boundaries.thrusters_seawater_supply.temperature = Stamped.stamp(15)

    control.to_cooling()

    result = await executor.tick(
        control.initial(executor.time()).values,
    )

    # stabilise
    for i in range(90):
        control_values = control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(control_values)

    for i in range(80):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_temperature_supply.temperature.value > 35


async def test_heat_dump_with_hot_sea(control, executor):
    executor._boundaries.thrusters_seawater_supply.temperature = Stamped.stamp(45)

    control.to_cooling()
    result = await executor.tick(
        control.initial(executor.time()).values,
    )

    # stabilise
    for i in range(90):
        control_values = control.control(
            result.sensor_values, executor.time()
        ).values
        result = await executor.tick(control_values)

    for i in range(80):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_temperature_supply.temperature.value < 65


async def test_pump_flow_recovery(control, executor):
    control.to_recovery()
    result = await executor.tick(
        control.initial(executor.time()).values,
    )

    # stabilise
    for i in range(20):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(80):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(10, abs=2)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(10, abs=2)

    executor._boundaries.thrusters_aft.active = Stamped.stamp(False)
    executor._boundaries.thrusters_aft.heat_flow = Stamped.stamp(0)

    # stabilise
    for i in range(120):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(80):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=2)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(10, abs=2)

    executor._boundaries.thrusters_fwd.active = Stamped.stamp(False)
    executor._boundaries.thrusters_fwd.heat_flow = Stamped.stamp(0)

    # stabilise
    for i in range(90):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(80):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=2)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(0, abs=2)


async def test_pump_flow_cooling(control, executor):
    control.to_cooling()
    result = await executor.tick(
        control.initial(executor.time()).values,
    )

    # stabilise
    for i in range(20):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(80):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(22, abs=2)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(22, abs=2)

    executor._boundaries.thrusters_aft.active = Stamped.stamp(False)
    executor._boundaries.thrusters_aft.heat_flow = Stamped.stamp(0)

    # stabilise
    for i in range(120):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(80):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=2)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(22, abs=2)

    executor._boundaries.thrusters_fwd.active = Stamped.stamp(False)
    executor._boundaries.thrusters_fwd.heat_flow = Stamped.stamp(0)

    # stabilise
    for i in range(90):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(80):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=2)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(0, abs=2)


async def test_pump_flow_safe(control, executor):
    control.to_safe()
    result = await executor.tick(
        control.initial(executor.time()).values,
    )

    # stabilise
    for i in range(20):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(80):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(22, abs=2)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(22, abs=2)

    executor._boundaries.thrusters_aft.active = Stamped.stamp(False)
    executor._boundaries.thrusters_aft.heat_flow = Stamped.stamp(0)

    # stabilise
    for i in range(20):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(80):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(22, abs=2)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(22, abs=2)

    executor._boundaries.thrusters_fwd.active = Stamped.stamp(False)
    executor._boundaries.thrusters_fwd.heat_flow = Stamped.stamp(0)

    # stabilise
    for i in range(20):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(80):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(22, abs=2)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(22, abs=2)
