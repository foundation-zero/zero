# test mode switching: from idle to cooling (raise warm temp) to idle (low warm temp) to cooling (raise warm temp) to idle (low cold temp)

from thrs.control.modules.fahrenheit import FahrenheitControl
from thrs.orchestration.executor import SimulationExecutor
from pytest import approx


async def test_state_mode_switches(
    control: FahrenheitControl, executor: SimulationExecutor
):
    # start with cooling demand and insufficient heat
    executor._simulation_inputs.fahreneit_available_hot_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_hot_minimum.temperature - 1
    )
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_cold_trigger.temperature + 1
    )

    result = await executor.tick(control.initial().values)
    control_values = control.control(result.sensor_values).values

    assert control.mode == "idle"

    # higher but still insufficient heat to trigger cooling
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_hot_minimum.temperature + 1
    )
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_cold_trigger.temperature + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "idle"

    # sufficient heat
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_hot_trigger.temperature + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "cooling"

    # sufficient but lower heat
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_hot_minimum.temperature + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "cooling"

    # insufficient heat
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_hot_minimum.temperature - 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "idle"

    # sufficient heat but no cooling demand
    executor._simulation_inputs.fahreneit_available_hot_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_hot_trigger.temperature + 1
    )
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_cold_minimum.temperature - 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "idle"

    # insufficient cooling demand
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_cold_trigger.temperature - 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "idle"

    # sufficient cooling demand to trigger cooling
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_cold_trigger.temperature + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "cooling"

    # sufficient cooling demand
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_cold_minimum.temperature + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "cooling"

    # no cooling demand
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature = (
        executor._simulation_inputs.fahrenheit_cold_minimum.temperature - 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == "idle"


async def test_cooling(control: FahrenheitControl, executor: SimulationExecutor):
    result = await executor.tick(control.initial().values)
    control_values = control.control(result.sensor_values).values

    assert control.mode == "cooling"

    for i in range(60):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert (
        result.sensor_values.fahrenheit_chiller_waste_in.temperature.value
        < result.sensor_values.fahrenheit_waste_out.temperature.value
    )
    assert (
        result.sensor_values.fahrenheit_chiller_cold_in.temperature.value
        > result.sensor_values.fahrenheit_cold_out.temperature.value
    )
    assert (
        result.sensor_values.fahrenheit_chiller_hot_in.temperature.value
        > result.sensor_values.fahrenheit_hot_out.temperature.value
    )


async def test_waste_recovery(control: FahrenheitControl, executor: SimulationExecutor):
    executor._simulation_inputs.fahrenheit_waste_supply.temperature = 25
    control._parameters.waste_recovery_temperature_setpoint = 30
    control._parameters.waste_cooling_temperature_setpoint = 40

    result = await executor.tick(control.initial().values)
    control_values = control.control(result.sensor_values).values

    for i in range(5 * 60):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert (
        result.sensor_values.fahrenheit_waste_out.temperature.value
        > result.sensor_values.fahrenheit_waste_in.temperature.value
    )
    assert result.sensor_values.fahrenheit_waste_out.temperature.value == approx(
        control._parameters.waste_recovery_temperature_setpoint, abs=1
    )


async def test_waste_cooling(control: FahrenheitControl, executor: SimulationExecutor):
    executor._simulation_inputs.fahrenheit_waste_supply.temperature = 40
    control._parameters.waste_recovery_temperature_setpoint = 10
    control._parameters.waste_cooling_temperature_setpoint = 35

    result = await executor.tick(control.initial().values)
    control_values = control.control(result.sensor_values).values

    for i in range(5 * 60):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert (
        result.sensor_values.fahrenheit_waste_out.temperature.value
        > result.sensor_values.fahrenheit_waste_in.temperature.value
    )
    assert result.sensor_values.fahrenheit_waste_in.temperature.value == approx(
        control._parameters.waste_cooling_temperature_setpoint, abs=1
    )
