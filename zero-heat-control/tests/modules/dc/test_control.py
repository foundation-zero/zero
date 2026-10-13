from pytest import approx

from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.control.modules.dc import DcControl, DcParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.input_output.definitions.simulation import Converter
from thrs.input_output.modules.dc import DcSensorValues, DcSimulationInputs


def test_all_idle(
    control: DcControl,
    runner: SimulationTestRunner,
    simulation_inputs_inactive: DcSimulationInputs,
):
    runner.update_simulation_inputs(simulation_inputs_inactive)  # type: ignore

    sensor_values, *_ = runner.run(90)

    assert control.mode.brightloops_aft.is_idle
    assert control.mode.brightloops_fwd.is_idle
    assert control.mode.ugrids.is_idle

    assert isinstance(sensor_values, DcSensorValues)
    for _, sensor in sensor_values:
        if isinstance(sensor, FlowSensor):
            assert sensor.flow.value == approx(0.0, abs=0.01)


def test_only_brightloops_aft(
    control: DcControl,
    runner: SimulationTestRunner,
    simulation_inputs_brightloops_aft_active: DcSimulationInputs,
):
    runner.update_simulation_inputs(  # type: ignore
        simulation_inputs_brightloops_aft_active
    )

    sensor_values, *_ = runner.run(180)

    assert control.mode.brightloops_aft.is_recovery
    assert control.mode.brightloops_fwd.is_idle
    assert control.mode.ugrids.is_idle

    assert isinstance(sensor_values, DcSensorValues)
    assert sensor_values.dc_flow_aft1.flow.value == approx(5, abs=0.1)
    assert sensor_values.dc_flow_aft2.flow.value == approx(5, abs=0.1)
    assert sensor_values.dc_flow_aft3.flow.value == approx(5, abs=0.1)
    assert sensor_values.dc_flow_aft4.flow.value == approx(5, abs=0.1)
    assert (
        sensor_values.dc_temperature_aft1_return.temperature.value
        > sensor_values.dc_temperature_aft_supply.temperature.value
    )


def test_only_one_brightloop(
    control: DcControl,
    runner: SimulationTestRunner,
    simulation_inputs_inactive: DcSimulationInputs,
):
    simulation_inputs_aft1_active = simulation_inputs_inactive.model_copy(
        update={
            "dc_brightloop_aft1": Converter(
                heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
            )
        }
    )
    runner.update_simulation_inputs(simulation_inputs_aft1_active)  # type: ignore

    sensor_values, *_ = runner.run(240)

    assert control.mode.brightloops_aft.is_recovery
    assert control.mode.brightloops_fwd.is_idle
    assert control.mode.ugrids.is_idle

    assert isinstance(sensor_values, DcSensorValues)
    assert sensor_values.dc_flow_aft1.flow.value == approx(5, abs=0.1)
    assert sensor_values.dc_flow_aft2.flow.value == approx(0, abs=0.1)
    assert sensor_values.dc_flow_aft3.flow.value == approx(0, abs=0.1)
    assert sensor_values.dc_flow_aft4.flow.value == approx(0, abs=0.1)
    assert (
        sensor_values.dc_temperature_aft1_return.temperature.value
        > sensor_values.dc_temperature_aft_supply.temperature.value
    )


def test_recovery(control: DcControl, runner: SimulationTestRunner):
    control.update_parameters(
        DcParameters(
            recovery_temperature=45,
            brightloop_return_temperature=45,
            ugrid_return_temperature=45,
        )
    )

    sensor_values, *_ = runner.run(1200)

    assert control.mode.brightloops_aft.is_recovery
    assert control.mode.brightloops_fwd.is_recovery
    assert control.mode.ugrids.is_recovery

    assert isinstance(sensor_values, DcSensorValues)
    assert (
        sensor_values.dc_temperature_aft1_return.temperature.value
        > sensor_values.dc_temperature_aft_supply.temperature.value
    )
    assert (
        sensor_values.dc_temperature_aft2_return.temperature.value
        > sensor_values.dc_temperature_aft_supply.temperature.value
    )
    assert (
        sensor_values.dc_temperature_aft3_return.temperature.value
        > sensor_values.dc_temperature_aft_supply.temperature.value
    )
    assert (
        sensor_values.dc_temperature_aft4_return.temperature.value
        > sensor_values.dc_temperature_aft_supply.temperature.value
    )
    assert (
        sensor_values.dc_temperature_fwd1_return.temperature.value
        > sensor_values.dc_temperature_fwd_supply.temperature.value
    )
    assert (
        sensor_values.dc_temperature_fwd2_return.temperature.value
        > sensor_values.dc_temperature_fwd_supply.temperature.value
    )
    assert (
        sensor_values.dc_temperature_ugrid1_return.temperature.value
        > sensor_values.dc_temperature_ugrid_supply.temperature.value
    )
    assert (
        sensor_values.dc_temperature_ugrid2_return.temperature.value
        > sensor_values.dc_temperature_ugrid_supply.temperature.value
    )

    assert sensor_values.dc_temperature_recovery.temperature.value == approx(45, abs=1)


def test_heat_dump(control: DcControl, runner: SimulationTestRunner):
    control.update_parameters(
        DcParameters(
            recovery_temperature=50,
            brightloop_return_temperature=50,
            ugrid_return_temperature=50,
            maximum_supply_temperature=45,
        )
    )

    sensor_values, *_ = runner.run(960)

    assert isinstance(sensor_values, DcSensorValues)
    assert sensor_values.dc_temperature_recovery.temperature.value == approx(50, abs=1)
    assert sensor_values.dc_temperature_supply.temperature.value == approx(45, abs=1)
