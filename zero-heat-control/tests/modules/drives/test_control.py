from pytest import approx

from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.control.modules.drives import DrivesControl, DrivesParameters
from thrs.input_output.definitions.control import Valve
from thrs.input_output.modules.drives import DrivesSensorValues, DrivesSimulationInputs


def test_idle(
    control: DrivesControl,
    runner: SimulationTestRunner,
    simulation_inputs_inactive: DrivesSimulationInputs,
):
    runner.update_simulation_inputs(simulation_inputs_inactive)  # type: ignore

    sensor_values, *_ = runner.run(90)

    assert control.mode.is_idle

    assert isinstance(sensor_values, DrivesSensorValues)
    assert sensor_values.drives_flow_propdrive_aft1.flow.value == approx(0.0, abs=0.01)
    assert sensor_values.drives_flow_propdrive_aft2.flow.value == approx(0.0, abs=0.01)
    assert sensor_values.drives_flow_propdrive_fwd1.flow.value == approx(0.0, abs=0.01)
    assert sensor_values.drives_flow_propdrive_fwd2.flow.value == approx(0.0, abs=0.01)
    assert sensor_values.drives_flow_shorepower.flow.value == approx(0.0, abs=0.01)
    assert sensor_values.drives_flow_recovery.flow.value == approx(0.0, abs=0.01)


def test_propulsion_all_active(
    control: DrivesControl,
    runner: SimulationTestRunner,
    simulation_inputs_all_drives_active: DrivesSimulationInputs,
):
    runner.update_simulation_inputs(simulation_inputs_all_drives_active)  # type: ignore

    sensor_values, *_ = runner.run(180)

    assert control.mode.is_propulsion

    assert isinstance(sensor_values, DrivesSensorValues)
    assert sensor_values.drives_flow_propdrive_aft1.flow.value == approx(15.0, abs=0.1)
    assert sensor_values.drives_flow_propdrive_aft2.flow.value == approx(15.0, abs=0.1)
    assert sensor_values.drives_flow_propdrive_fwd1.flow.value == approx(15.0, abs=0.1)
    assert sensor_values.drives_flow_propdrive_fwd2.flow.value == approx(15.0, abs=0.1)
    assert (
        sensor_values.drives_temperature_propdrive_aft1_return.temperature.value
        > sensor_values.drives_temperature_propdrives_aft_supply.temperature.value
    )
    assert (
        sensor_values.drives_temperature_propdrive_aft2_return.temperature.value
        > sensor_values.drives_temperature_propdrives_aft_supply.temperature.value
    )
    assert (
        sensor_values.drives_temperature_propdrive_fwd1_return.temperature.value
        > sensor_values.drives_temperature_propdrives_fwd_supply.temperature.value
    )
    assert (
        sensor_values.drives_temperature_propdrive_fwd2_return.temperature.value
        > sensor_values.drives_temperature_propdrives_fwd_supply.temperature.value
    )


def test_shorepower(
    control: DrivesControl,
    runner: SimulationTestRunner,
    simulation_inputs_shorepower: DrivesSimulationInputs,
):
    runner.update_simulation_inputs(simulation_inputs_shorepower)  # type: ignore

    sensor_values, *_ = runner.run(180)

    assert control.mode.is_shorepower

    assert isinstance(sensor_values, DrivesSensorValues)
    assert sensor_values.drives_flow_shorepower.flow.value == approx(20.0, abs=0.5)
    assert (
        sensor_values.drives_temperature_shorepower_return.temperature.value
        > sensor_values.drives_temperature_supply.temperature.value
    )


def test_heat_dump(
    control: DrivesControl,
    runner: SimulationTestRunner,
    simulation_inputs_shorepower: DrivesSimulationInputs,
):
    runner.update_simulation_inputs(simulation_inputs_shorepower)  # type: ignore
    control.update_parameters(
        DrivesParameters(
            shorepower_maximum_supply_temperature=30,
            recovery_temperature=100,  # don't recover, dump all heat
        )
    )

    sensor_values, *_ = runner.run(120)

    assert isinstance(sensor_values, DrivesSensorValues)
    assert sensor_values.drives_mix_recovery.position_rel.value == approx(
        Valve.MIXING_B_TO_AB, abs=0.01
    )
    assert sensor_values.drives_temperature_shorepower_return.temperature.value > 30.0
    assert sensor_values.drives_temperature_supply.temperature.value == approx(
        30.0, abs=1
    )


def test_heat_recovery(
    control: DrivesControl,
    runner: SimulationTestRunner,
    simulation_inputs_shorepower: DrivesSimulationInputs,
):
    runner.update_simulation_inputs(simulation_inputs_shorepower)  # type: ignore
    control.update_parameters(
        DrivesParameters(
            shorepower_maximum_supply_temperature=90,
            recovery_temperature=50,
        )
    )

    sensor_values, *_ = runner.run(720)

    assert isinstance(sensor_values, DrivesSensorValues)
    assert sensor_values.drives_temperature_recovery.temperature.value == approx(
        50.0, abs=1
    )
    assert (
        sensor_values.drives_temperature_recovery_mix.temperature.value
        < sensor_values.drives_temperature_recovery.temperature.value
    )


def test_flow_balancing(
    control: DrivesControl,
    runner: SimulationTestRunner,
    simulation_inputs_all_drives_active: DrivesSimulationInputs,
):
    runner.update_simulation_inputs(simulation_inputs_all_drives_active)  # type: ignore

    sensor_values, *_ = runner.run(120)

    assert control.mode.is_propulsion

    assert isinstance(sensor_values, DrivesSensorValues)
    assert sensor_values.drives_flow_propdrive_aft1.flow.value == approx(15.0, abs=0.5)
    assert sensor_values.drives_flow_propdrive_aft2.flow.value == approx(15.0, abs=0.5)
    assert sensor_values.drives_flow_propdrive_fwd1.flow.value == approx(15.0, abs=0.5)
    assert sensor_values.drives_flow_propdrive_fwd2.flow.value == approx(15.0, abs=0.5)
