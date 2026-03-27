from pytest import approx

from thrs.control.modules.lt1 import Lt1Control, Lt1Parameters
from thrs.input_output.definitions.control import Valve
from thrs.input_output.modules.lt1 import Lt1SimulationInputs
from thrs.orchestration.cycler import Cycler
from thrs.orchestration.executor import SimulationExecutionResult


async def test_idle(cycler: Cycler, simulation_inputs_inactive: Lt1SimulationInputs):
    cycler.update_simulation_inputs(simulation_inputs_inactive)

    result = await cycler.run(90)

    assert isinstance(cycler._control, Lt1Control)
    assert cycler._control.mode.is_idle

    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.lt1_flow_supply.flow.value == approx(0.0, abs=0.01)
    assert result.sensor_values.lt1_flow_recovery.flow.value == approx(0.0, abs=0.01)


async def test_propulsion_all_active(
    cycler: Cycler, simulation_inputs_all_drives_active: Lt1SimulationInputs
):
    cycler.update_simulation_inputs(simulation_inputs_all_drives_active)

    result = await cycler.run(90)

    assert isinstance(cycler._control, Lt1Control)
    assert cycler._control.mode.is_propulsion

    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.lt1_flow_supply.flow.value == approx(60.0, abs=0.01)
    assert result.sensor_values.lt1_flow_propdrive_aft.flow.value == approx(
        30.0, abs=0.01
    )
    assert result.sensor_values.lt1_flow_propdrive_fwd.flow.value == approx(
        30.0, abs=0.01
    )
    assert result.sensor_values.lt1_flow_propdrive_aft1.flow.value == approx(
        15.0, abs=0.01
    )
    assert result.sensor_values.lt1_flow_propdrive_aft2.flow.value == approx(
        15.0, abs=0.01
    )
    assert result.sensor_values.lt1_flow_propdrive_fwd1.flow.value == approx(
        15.0, abs=0.01
    )
    assert result.sensor_values.lt1_flow_propdrive_fwd2.flow.value == approx(
        15.0, abs=0.01
    )
    assert (
        result.sensor_values.lt1_temperature_propdrive_aft1_return.temperature.value
        > result.sensor_values.lt1_temperature_propdrive_aft_supply.temperature.value
    )
    assert (
        result.sensor_values.lt1_temperature_propdrive_aft2_return.temperature.value
        > result.sensor_values.lt1_temperature_propdrive_aft_supply.temperature.value
    )
    assert (
        result.sensor_values.lt1_temperature_propdrive_fwd1_return.temperature.value
        > result.sensor_values.lt1_temperature_propdrive_fwd_supply.temperature.value
    )
    assert (
        result.sensor_values.lt1_temperature_propdrive_fwd2_return.temperature.value
        > result.sensor_values.lt1_temperature_propdrive_fwd_supply.temperature.value
    )


async def test_shorepower(
    cycler: Cycler, simulation_inputs_shorepower: Lt1SimulationInputs
):
    cycler.update_simulation_inputs(simulation_inputs_shorepower)

    result = await cycler.run(90)

    assert isinstance(cycler._control, Lt1Control)
    assert cycler._control.mode.is_shorepower

    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.lt1_flow_supply.flow.value == approx(20.0, abs=0.01)
    assert result.sensor_values.lt1_flow_shorepower.flow.value == approx(20.0, abs=0.01)
    assert (
        result.sensor_values.lt1_temperature_shorepower_return.temperature.value
        > result.sensor_values.lt1_temperature_supply.temperature.value
    )


async def test_heat_dump(
    cycler: Cycler, simulation_inputs_shorepower: Lt1SimulationInputs
):
    cycler.update_simulation_inputs(simulation_inputs_shorepower)
    cycler._control.update_parameters(
        Lt1Parameters(
            shorepower_maximum_supply_temperature=30,
            recovery_temperature=100,  # don't recover, dump all heat
        )
    )

    result = await cycler.run(90)

    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.lt1_mix_recovery.setpoint.value == approx(
        Valve.MIXING_B_TO_AB, abs=0.01
    )
    assert (
        result.sensor_values.lt1_temperature_shorepower_return.temperature.value > 30.0
    )
    assert result.sensor_values.lt1_temperature_supply.temperature.value == approx(
        30.0, abs=0.01
    )


# TODO test_recovery_mixing

# TODO def test_flow_balancing
