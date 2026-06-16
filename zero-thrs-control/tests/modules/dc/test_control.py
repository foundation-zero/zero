from pytest import approx

from thrs.control.modules.dc import DcControl, DcParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.input_output.definitions.simulation import Converter
from thrs.input_output.modules.dc import DcSimulationInputs
from thrs.orchestration.connector import ExecutionResult
from thrs.orchestration.runner import Runner


async def test_all_idle(runner: Runner, simulation_inputs_inactive: DcSimulationInputs):
    runner._connector.update_simulation_inputs(simulation_inputs_inactive)  # type: ignore

    await runner.run(90)
    result = runner.last_tick_result

    assert isinstance(runner._control, DcControl)
    assert runner._control.mode.brightloops_aft.is_idle
    assert runner._control.mode.brightloops_fwd.is_idle
    assert runner._control.mode.ugrids.is_idle

    assert isinstance(result, ExecutionResult)
    for _, sensor in result.sensor_values:
        if isinstance(sensor, FlowSensor):
            assert sensor.flow.value == approx(0.0, abs=0.01)


async def test_only_brightloops_aft(
    runner: Runner, simulation_inputs_brightloops_aft_active: DcSimulationInputs
):
    runner._connector.update_simulation_inputs(  # type: ignore
        simulation_inputs_brightloops_aft_active
    )

    await runner.run(180)
    result = runner.last_tick_result

    assert isinstance(runner._control, DcControl)
    assert runner._control.mode.brightloops_aft.is_recovery
    assert runner._control.mode.brightloops_fwd.is_idle
    assert runner._control.mode.ugrids.is_idle

    assert isinstance(result, ExecutionResult)
    assert result.sensor_values.dc_flow_aft1.flow.value == approx(5, abs=0.1)
    assert result.sensor_values.dc_flow_aft2.flow.value == approx(5, abs=0.1)
    assert result.sensor_values.dc_flow_aft3.flow.value == approx(5, abs=0.1)
    assert result.sensor_values.dc_flow_aft4.flow.value == approx(5, abs=0.1)
    assert (
        result.sensor_values.dc_temperature_aft1_return.temperature.value
        > result.sensor_values.dc_temperature_aft_supply.temperature.value
    )


async def test_only_one_brightloop(
    runner: Runner, simulation_inputs_inactive: DcSimulationInputs
):
    simulation_inputs_aft1_active = simulation_inputs_inactive.model_copy(
        update={
            "dc_brightloop_aft1": Converter(
                heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
            )
        }
    )
    runner._connector.update_simulation_inputs(simulation_inputs_aft1_active)  # type: ignore

    await runner.run(240)
    result = runner.last_tick_result

    assert isinstance(runner._control, DcControl)
    assert runner._control.mode.brightloops_aft.is_recovery
    assert runner._control.mode.brightloops_fwd.is_idle
    assert runner._control.mode.ugrids.is_idle

    assert isinstance(result, ExecutionResult)
    assert result.sensor_values.dc_flow_aft1.flow.value == approx(5, abs=0.1)
    assert result.sensor_values.dc_flow_aft2.flow.value == approx(0, abs=0.1)
    assert result.sensor_values.dc_flow_aft3.flow.value == approx(0, abs=0.1)
    assert result.sensor_values.dc_flow_aft4.flow.value == approx(0, abs=0.1)
    assert (
        result.sensor_values.dc_temperature_aft1_return.temperature.value
        > result.sensor_values.dc_temperature_aft_supply.temperature.value
    )


async def test_recovery(runner: Runner):
    runner._control.update_parameters(
        DcParameters(
            recovery_temperature=45,
            brightloop_return_temperature=45,
            ugrid_return_temperature=45,
        )
    )

    await runner.run(1200)
    result = runner.last_tick_result

    assert isinstance(runner._control, DcControl)
    assert runner._control.mode.brightloops_aft.is_recovery
    assert runner._control.mode.brightloops_fwd.is_recovery
    assert runner._control.mode.ugrids.is_recovery

    assert isinstance(result, ExecutionResult)
    assert (
        result.sensor_values.dc_temperature_aft1_return.temperature.value
        > result.sensor_values.dc_temperature_aft_supply.temperature.value
    )
    assert (
        result.sensor_values.dc_temperature_aft2_return.temperature.value
        > result.sensor_values.dc_temperature_aft_supply.temperature.value
    )
    assert (
        result.sensor_values.dc_temperature_aft3_return.temperature.value
        > result.sensor_values.dc_temperature_aft_supply.temperature.value
    )
    assert (
        result.sensor_values.dc_temperature_aft4_return.temperature.value
        > result.sensor_values.dc_temperature_aft_supply.temperature.value
    )
    assert (
        result.sensor_values.dc_temperature_fwd1_return.temperature.value
        > result.sensor_values.dc_temperature_fwd_supply.temperature.value
    )
    assert (
        result.sensor_values.dc_temperature_fwd2_return.temperature.value
        > result.sensor_values.dc_temperature_fwd_supply.temperature.value
    )
    assert (
        result.sensor_values.dc_temperature_ugrid1_return.temperature.value
        > result.sensor_values.dc_temperature_ugrid_supply.temperature.value
    )
    assert (
        result.sensor_values.dc_temperature_ugrid2_return.temperature.value
        > result.sensor_values.dc_temperature_ugrid_supply.temperature.value
    )

    assert result.sensor_values.dc_temperature_recovery.temperature.value == approx(
        45, abs=1
    )


async def test_heat_dump(runner: Runner):
    runner._control.update_parameters(
        DcParameters(
            recovery_temperature=50,
            brightloop_return_temperature=50,
            ugrid_return_temperature=50,
            maximum_supply_temperature=45,
        )
    )

    await runner.run(960)
    result = runner.last_tick_result

    assert isinstance(result, ExecutionResult)
    assert result.sensor_values.dc_temperature_recovery.temperature.value == approx(
        50, abs=1
    )
    assert result.sensor_values.dc_temperature_supply.temperature.value == approx(
        45, abs=1
    )
