# test mode switching: from idle to cooling (raise warm temp) to idle (low warm temp) to cooling (raise warm temp) to idle (low cold temp)

from thrs.control.modules.fahrenheit import FahrenheitControl
from thrs.orchestration.executor import SimulationExecutor
from pytest import approx


async def test_state_mode_switches(
    control: FahrenheitControl, executor: SimulationExecutor
):
    # start with cooling demand and insufficient heat
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature.value = (
        control._parameters.fahrenheit_hot_minimum - 1
    )
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature.value = (
        control._parameters.fahrenheit_cold_trigger + 1
    )

    result = await executor.tick(control.initial().values)
    control_values = control.control(result.sensor_values).values

    assert control.mode == "idle"
    result = await executor.tick(control_values)

    # higher but still insufficient heat to trigger cooling
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature.value = (
        control._parameters.fahrenheit_hot_minimum + 1
    )
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature.value = (
        control._parameters.fahrenheit_cold_trigger + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "idle"

    # sufficient heat
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature.value = (
        control._parameters.fahrenheit_hot_trigger + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "cooling"

    # sufficient but lower heat
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature.value = (
        control._parameters.fahrenheit_hot_minimum + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "cooling"

    # insufficient heat
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature.value = (
        control._parameters.fahrenheit_hot_minimum - 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "idle"

    # sufficient heat but no cooling demand
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature.value = (
        control._parameters.fahrenheit_hot_trigger + 1
    )
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature.value = (
        control._parameters.fahrenheit_cold_minimum - 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "idle"

    # insufficient cooling demand
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature.value = (
        control._parameters.fahrenheit_cold_trigger - 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "idle"

    # sufficient cooling demand to trigger cooling
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature.value = (
        control._parameters.fahrenheit_cold_trigger + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "cooling"

    # sufficient cooling demand
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature.value = (
        control._parameters.fahrenheit_cold_minimum + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "cooling"

    # no cooling demand
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature.value = (
        control._parameters.fahrenheit_cold_minimum - 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "idle"


async def test_fahrenheit_cooling(
    control: FahrenheitControl, executor: SimulationExecutor
):
    result = await executor.tick(control.initial().values)

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "cooling"

    for i in range(100):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert (
        result.sensor_values.fahrenheit_chiller.temperature_waste_in.value
        < result.sensor_values.fahrenheit_chiller.temperature_waste_out.value
    )
    assert (
        result.sensor_values.fahrenheit_chiller.temperature_cold_in.value
        > result.sensor_values.fahrenheit_chiller.temperature_cold_out.value
    )
    assert (
        result.sensor_values.fahrenheit_chiller.temperature_hot_in.value
        > result.sensor_values.fahrenheit_chiller.temperature_hot_out.value
    )


async def test_waste_recovery(control: FahrenheitControl, executor: SimulationExecutor):
    executor._simulation_inputs.fahrenheit_boilers_supply.temperature.value = 10
    control._parameters.waste_recovery_temperature_setpoint = 30
    control._parameters.waste_cooling_temperature_setpoint = 60

    result = await executor.tick(control.initial().values)

    for i in range(100):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "cooling"

    for i in range(5 * 60):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert (
        result.sensor_values.fahrenheit_chiller.temperature_waste_out.value
        > result.sensor_values.fahrenheit_chiller.temperature_waste_in.value
    )
    assert (
        result.sensor_values.fahrenheit_chiller.temperature_waste_out.value
        == approx(control._parameters.waste_recovery_temperature_setpoint, abs=1)
    )


async def test_waste_cooling(control: FahrenheitControl, executor: SimulationExecutor):
    executor._simulation_inputs.fahrenheit_boilers_supply.temperature.value = 40
    executor._simulation_inputs.fahrenheit_seawater_supply.temperature.value = 10
    control._parameters.waste_recovery_temperature_setpoint = 10
    control._parameters.waste_cooling_temperature_setpoint = 35

    result = await executor.tick(control.initial().values)

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "cooling"

    for i in range(5 * 60):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert (
        result.sensor_values.fahrenheit_chiller.temperature_waste_out.value
        > result.sensor_values.fahrenheit_chiller.temperature_waste_in.value
    )
    assert result.sensor_values.fahrenheit_chiller.temperature_waste_in.value == approx(
        control._parameters.waste_cooling_temperature_setpoint, abs=1
    )
