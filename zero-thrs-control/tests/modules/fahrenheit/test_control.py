from datetime import datetime, timedelta

from thrs.control.modules.fahrenheit import (
    FahrenheitControl,
    FahrenheitControlMode,
    FahrenheitParameters,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    Fahrenheit,
    TemperatureBoundary,
)
from thrs.input_output.modules.fahrenheit import FahrenheitSimulationInputs
from thrs.orchestration.executor import SimulationExecutor
from pytest import approx

from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import fahrenheit_path


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

    assert control.mode == FahrenheitControlMode(mode="idle")
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

    assert control.mode == FahrenheitControlMode(mode="idle")

    # sufficient heat
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature.value = (
        control._parameters.fahrenheit_hot_trigger + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == FahrenheitControlMode(mode="cooling")

    # sufficient but lower heat
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature.value = (
        control._parameters.fahrenheit_hot_minimum + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == FahrenheitControlMode(mode="cooling")

    # insufficient heat
    executor._simulation_inputs.fahrenheit_available_hot_temperature.temperature.value = (
        control._parameters.fahrenheit_hot_minimum - 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == FahrenheitControlMode(mode="idle")

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

    assert control.mode == FahrenheitControlMode(mode="idle")

    # insufficient cooling demand
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature.value = (
        control._parameters.fahrenheit_cold_trigger - 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == FahrenheitControlMode(mode="idle")

    # sufficient cooling demand to trigger cooling
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature.value = (
        control._parameters.fahrenheit_cold_trigger + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == FahrenheitControlMode(mode="cooling")

    # sufficient cooling demand
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature.value = (
        control._parameters.fahrenheit_cold_minimum + 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == FahrenheitControlMode(mode="cooling")

    # no cooling demand
    executor._simulation_inputs.fahrenheit_available_cold_temperature.temperature.value = (
        control._parameters.fahrenheit_cold_minimum - 1
    )

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == FahrenheitControlMode(mode="idle")


async def test_fahrenheit_cooling(
    control: FahrenheitControl, executor: SimulationExecutor
):
    result = await executor.tick(control.initial().values)

    for i in range(10):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == FahrenheitControlMode(mode="cooling")

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
    executor._simulation_inputs.fahrenheit_boilers_supply.temperature.value = 20
    control._parameters.waste_recovery_temperature_setpoint = 40
    control._parameters.waste_cooling_temperature_setpoint = 60

    result = await executor.tick(control.initial().values)

    for i in range(100):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == FahrenheitControlMode(mode="cooling")

    for i in range(5 * 60):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

        assert (
            result.sensor_values.fahrenheit_chiller.temperature_waste_out.value
            == approx(
                control._parameters.waste_recovery_temperature_setpoint, abs=10
            )  # Very high margin due to fluctuating temperatures
        )


async def test_waste_cooling(io_mapping):
    simulation_inputs = FahrenheitSimulationInputs(
        fahrenheit_cold_supply=TemperatureBoundary(temperature=Stamped.stamp(20.0)),
        fahrenheit_seawater_supply=Boundary(
            temperature=Stamped.stamp(10.0), flow=Stamped.stamp(64.0)
        ),
        fahrenheit_available_cold_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(20.0)
        ),
        fahrenheit_available_hot_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(65.0)
        ),
        fahrenheit_available_seawater_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(30.0)
        ),
        fahrenheit_chiller=Fahrenheit(free_cooling=Stamped.stamp(False)),
        fahrenheit_ht_supply=Boundary(
            temperature=Stamped.stamp(60.0), flow=Stamped.stamp(42.0)
        ),
        fahrenheit_boilers_supply=Boundary(
            temperature=Stamped.stamp(10.0), flow=Stamped.stamp(45.0)
        ),
    )
    parameters = FahrenheitParameters(
        waste_recovery_temperature_setpoint=10,
        waste_cooling_temperature_setpoint=20,
    )

    with Fmu(fahrenheit_path) as fmu:
        executor = SimulationExecutor(
            io_mapping,
            fmu,
            simulation_inputs,
            datetime.fromtimestamp(0),
            timedelta(seconds=1),
        )
        control = FahrenheitControl(parameters, executor.time)

        result = await executor.tick(control.initial().values)

        for i in range(100):
            control_values = control.control(result.sensor_values).values
            result = await executor.tick(control_values)

        assert control.mode == FahrenheitControlMode(mode="cooling")

        for i in range(5 * 60):
            control_values = control.control(result.sensor_values).values
            result = await executor.tick(control_values)

            assert (
                result.sensor_values.fahrenheit_chiller.temperature_waste_in.value
                == approx(
                    control._parameters.waste_cooling_temperature_setpoint,
                    abs=12,  # Very high margin due to fluctuating temperatures
                )
            )
