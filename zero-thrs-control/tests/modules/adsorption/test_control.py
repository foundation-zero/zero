from datetime import datetime, timedelta

from pytest import approx

from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.adsorption import (
    AdsorptionControl,
    AdsorptionControlMode,
    AdsorptionParameters,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    AdsorptionChiller,
    Boundary,
    TemperatureBoundary,
)
from thrs.input_output.modules.adsorption import (
    AdsorptionSensorValues,
    AdsorptionSimulationInputs,
    AdsorptionSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import adsorption_path


def test_state_mode_switches(
    control: AdsorptionControl,
    simulation: Simulation,
    simulation_inputs: AdsorptionSimulationInputs,
):
    # start with cooling demand and insufficient heat
    simulation_inputs.adsorption_available_hot_temperature.temperature.value = (
        control.parameters.adsorption_hot_minimum - 1
    )
    simulation_inputs.adsorption_available_cold_temperature.temperature.value = (
        control.parameters.adsorption_cold_trigger + 1
    )

    result = simulation.tick(control.initial()[0])
    control_values, _ = control.control(result.sensor_values)

    assert control.mode == AdsorptionControlMode(mode="idle")
    result = simulation.tick(control_values)

    # higher but still insufficient heat to trigger cooling
    simulation_inputs.adsorption_available_hot_temperature.temperature.value = (
        control.parameters.adsorption_hot_minimum + 1
    )
    simulation_inputs.adsorption_available_cold_temperature.temperature.value = (
        control.parameters.adsorption_cold_trigger + 1
    )

    for _i in range(10):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == AdsorptionControlMode(mode="idle")

    # sufficient heat
    simulation_inputs.adsorption_available_hot_temperature.temperature.value = (
        control.parameters.adsorption_hot_trigger + 1
    )

    for _i in range(10):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == AdsorptionControlMode(mode="cooling")

    # sufficient but lower heat
    simulation_inputs.adsorption_available_hot_temperature.temperature.value = (
        control.parameters.adsorption_hot_minimum + 1
    )

    for _i in range(10):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == AdsorptionControlMode(mode="cooling")

    # insufficient heat
    simulation_inputs.adsorption_available_hot_temperature.temperature.value = (
        control.parameters.adsorption_hot_minimum - 1
    )

    for _i in range(10):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == AdsorptionControlMode(mode="idle")

    # sufficient heat but no cooling demand
    simulation_inputs.adsorption_available_hot_temperature.temperature.value = (
        control.parameters.adsorption_hot_trigger + 1
    )
    simulation_inputs.adsorption_available_cold_temperature.temperature.value = (
        control.parameters.adsorption_cold_minimum - 1
    )

    for _i in range(10):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == AdsorptionControlMode(mode="idle")

    # insufficient cooling demand
    simulation_inputs.adsorption_available_cold_temperature.temperature.value = (
        control.parameters.adsorption_cold_trigger - 1
    )

    for _i in range(10):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == AdsorptionControlMode(mode="idle")

    # sufficient cooling demand to trigger cooling
    simulation_inputs.adsorption_available_cold_temperature.temperature.value = (
        control.parameters.adsorption_cold_trigger + 1
    )

    for _i in range(10):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == AdsorptionControlMode(mode="cooling")

    # sufficient cooling demand
    simulation_inputs.adsorption_available_cold_temperature.temperature.value = (
        control.parameters.adsorption_cold_minimum + 1
    )

    for _i in range(10):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == AdsorptionControlMode(mode="cooling")

    # no cooling demand
    simulation_inputs.adsorption_available_cold_temperature.temperature.value = (
        control.parameters.adsorption_cold_minimum - 1
    )

    for _i in range(10):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == AdsorptionControlMode(mode="idle")


def test_adsorption_cooling(control: AdsorptionControl, simulation: Simulation):
    result = simulation.tick(control.initial()[0])

    for _i in range(10):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == AdsorptionControlMode(mode="cooling")

    for _i in range(100):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert (
        result.sensor_values.adsorption_chiller.temperature_waste_in.value
        < result.sensor_values.adsorption_chiller.temperature_waste_out.value
    )
    assert (
        result.sensor_values.adsorption_chiller.temperature_cold_in.value
        > result.sensor_values.adsorption_chiller.temperature_cold_out.value
    )
    assert (
        result.sensor_values.adsorption_chiller.temperature_hot_in.value
        > result.sensor_values.adsorption_chiller.temperature_hot_out.value
    )


def test_waste_recovery(
    control: AdsorptionControl,
    simulation: Simulation,
    simulation_inputs: AdsorptionSimulationInputs,
):
    simulation_inputs.adsorption_dhw_supply.temperature.value = 20
    control.parameters.waste_recovery_temperature_setpoint = 40
    control.parameters.waste_cooling_temperature_setpoint = 60

    result = simulation.tick(control.initial()[0])

    for _i in range(100):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == AdsorptionControlMode(mode="cooling")

    for _i in range(5 * 60):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

        assert (
            result.sensor_values.adsorption_chiller.temperature_waste_out.value
            == approx(
                control.parameters.waste_recovery_temperature_setpoint, abs=10
            )  # Very high margin due to fluctuating temperatures
        )


def test_waste_cooling():
    simulation_inputs = AdsorptionSimulationInputs(
        adsorption_cooling_supply=TemperatureBoundary(temperature=Stamped.stamp(20.0)),
        adsorption_seawater_supply=Boundary(
            temperature=Stamped.stamp(10.0), flow=Stamped.stamp(64.0)
        ),
        adsorption_available_cold_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(20.0)
        ),
        adsorption_available_hot_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(65.0)
        ),
        adsorption_available_seawater_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(30.0)
        ),
        adsorption_chiller=AdsorptionChiller(free_cooling=Stamped.stamp(False)),
        adsorption_consumers_supply=Boundary(
            temperature=Stamped.stamp(60.0), flow=Stamped.stamp(42.0)
        ),
        adsorption_dhw_supply=Boundary(
            temperature=Stamped.stamp(10.0), flow=Stamped.stamp(45.0)
        ),
    )
    parameters = AdsorptionParameters(
        waste_recovery_temperature_setpoint=10,
        waste_cooling_temperature_setpoint=20,
    )

    with Fmu(adsorption_path) as fmu:
        simulation = Simulation(
            AdsorptionSensorValues,
            AdsorptionSimulationOutputs,
            fmu,
            simulation_inputs,
            datetime.fromtimestamp(0),
            timedelta(seconds=1),
        )
        control = AdsorptionControl(
            parameters, simulation.time, MachineStateLoggingServiceNoop()
        )

        result = simulation.tick(control.initial()[0])

        for _i in range(100):
            control_values, _ = control.control(result.sensor_values)
            result = simulation.tick(control_values)

        assert control.mode == AdsorptionControlMode(mode="cooling")

        for _i in range(5 * 60):
            control_values, _ = control.control(result.sensor_values)
            result = simulation.tick(control_values)

            assert (
                result.sensor_values.adsorption_chiller.temperature_waste_in.value
                == approx(
                    control.parameters.waste_cooling_temperature_setpoint,
                    abs=12,  # Very high margin due to fluctuating temperatures
                )
            )
