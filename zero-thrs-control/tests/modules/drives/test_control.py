from pytest import approx

from thrs.control.modules.drives import DrivesControl, DrivesParameters
from thrs.input_output.definitions.control import Valve
from thrs.input_output.modules.drives import DrivesSimulationInputs
from thrs.orchestration.connector import ExecutionResult
from thrs.orchestration.runner import Runner


async def test_idle(runner: Runner, simulation_inputs_inactive: DrivesSimulationInputs):
    runner._connector.update_simulation_inputs(simulation_inputs_inactive)  # type: ignore

    await runner.run(90)
    result = runner.last_tick_result

    assert isinstance(runner._control, DrivesControl)
    assert runner._control.mode.is_idle

    assert isinstance(result, ExecutionResult)
    assert result.sensor_values.drives_flow_propdrive_aft1.flow.value == approx(
        0.0, abs=0.01
    )
    assert result.sensor_values.drives_flow_propdrive_aft2.flow.value == approx(
        0.0, abs=0.01
    )
    assert result.sensor_values.drives_flow_propdrive_fwd1.flow.value == approx(
        0.0, abs=0.01
    )
    assert result.sensor_values.drives_flow_propdrive_fwd2.flow.value == approx(
        0.0, abs=0.01
    )
    assert result.sensor_values.drives_flow_shorepower.flow.value == approx(
        0.0, abs=0.01
    )
    assert result.sensor_values.drives_flow_recovery.flow.value == approx(0.0, abs=0.01)


async def test_propulsion_all_active(
    runner: Runner, simulation_inputs_all_drives_active: DrivesSimulationInputs
):
    runner._connector.update_simulation_inputs(simulation_inputs_all_drives_active)  # type: ignore

    await runner.run(180)
    result = runner.last_tick_result

    assert isinstance(runner._control, DrivesControl)
    assert runner._control.mode.is_propulsion

    assert isinstance(result, ExecutionResult)
    assert result.sensor_values.drives_flow_propdrive_aft1.flow.value == approx(
        15.0, abs=0.1
    )
    assert result.sensor_values.drives_flow_propdrive_aft2.flow.value == approx(
        15.0, abs=0.1
    )
    assert result.sensor_values.drives_flow_propdrive_fwd1.flow.value == approx(
        15.0, abs=0.1
    )
    assert result.sensor_values.drives_flow_propdrive_fwd2.flow.value == approx(
        15.0, abs=0.1
    )
    assert (
        result.sensor_values.drives_temperature_propdrive_aft1_return.temperature.value
        > result.sensor_values.drives_temperature_propdrives_aft_supply.temperature.value
    )
    assert (
        result.sensor_values.drives_temperature_propdrive_aft2_return.temperature.value
        > result.sensor_values.drives_temperature_propdrives_aft_supply.temperature.value
    )
    assert (
        result.sensor_values.drives_temperature_propdrive_fwd1_return.temperature.value
        > result.sensor_values.drives_temperature_propdrives_fwd_supply.temperature.value
    )
    assert (
        result.sensor_values.drives_temperature_propdrive_fwd2_return.temperature.value
        > result.sensor_values.drives_temperature_propdrives_fwd_supply.temperature.value
    )


async def test_shorepower(
    runner: Runner, simulation_inputs_shorepower: DrivesSimulationInputs
):
    runner._connector.update_simulation_inputs(simulation_inputs_shorepower)  # type: ignore

    await runner.run(180)
    result = runner.last_tick_result

    assert isinstance(runner._control, DrivesControl)
    assert runner._control.mode.is_shorepower

    assert isinstance(result, ExecutionResult)
    assert result.sensor_values.drives_flow_shorepower.flow.value == approx(
        20.0, abs=0.5
    )
    assert (
        result.sensor_values.drives_temperature_shorepower_return.temperature.value
        > result.sensor_values.drives_temperature_supply.temperature.value
    )


async def test_heat_dump(
    runner: Runner, simulation_inputs_shorepower: DrivesSimulationInputs
):
    runner._connector.update_simulation_inputs(simulation_inputs_shorepower)  # type: ignore
    runner._control.update_parameters(
        DrivesParameters(
            shorepower_maximum_supply_temperature=30,
            recovery_temperature=100,  # don't recover, dump all heat
        )
    )

    await runner.run(120)
    result = runner.last_tick_result

    assert isinstance(result, ExecutionResult)
    assert result.sensor_values.drives_mix_recovery.position_rel.value == approx(
        Valve.MIXING_B_TO_AB, abs=0.01
    )
    assert (
        result.sensor_values.drives_temperature_shorepower_return.temperature.value
        > 30.0
    )
    assert result.sensor_values.drives_temperature_supply.temperature.value == approx(
        30.0, abs=1
    )


async def test_heat_recovery(
    runner: Runner, simulation_inputs_shorepower: DrivesSimulationInputs
):
    runner._connector.update_simulation_inputs(simulation_inputs_shorepower)  # type: ignore
    runner._control.update_parameters(
        DrivesParameters(
            shorepower_maximum_supply_temperature=90,
            recovery_temperature=50,
        )
    )

    await runner.run(720)
    result = runner.last_tick_result

    assert isinstance(result, ExecutionResult)
    assert result.sensor_values.drives_temperature_recovery.temperature.value == approx(
        50.0, abs=1
    )
    assert (
        result.sensor_values.drives_temperature_recovery_mix.temperature.value
        < result.sensor_values.drives_temperature_recovery.temperature.value
    )


async def test_flow_balancing(
    runner: Runner, simulation_inputs_all_drives_active: DrivesSimulationInputs
):
    runner._connector.update_simulation_inputs(simulation_inputs_all_drives_active)  # type: ignore

    await runner.run(120)
    result = runner.last_tick_result

    assert isinstance(runner._control, DrivesControl)
    assert runner._control.mode.is_propulsion

    assert isinstance(result, ExecutionResult)
    assert result.sensor_values.drives_flow_propdrive_aft1.flow.value == approx(
        15.0, abs=0.5
    )
    assert result.sensor_values.drives_flow_propdrive_aft2.flow.value == approx(
        15.0, abs=0.5
    )
    assert result.sensor_values.drives_flow_propdrive_fwd1.flow.value == approx(
        15.0, abs=0.5
    )
    assert result.sensor_values.drives_flow_propdrive_fwd2.flow.value == approx(
        15.0, abs=0.5
    )
