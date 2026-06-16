from pytest import approx

from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.control.modules.dhw import (
    DhwControl,
    TanksController,
)
from thrs.input_output.base import Stamped
from thrs.input_output.modules.dhw import (
    DhwSimulationInputs,
)
from thrs.orchestration.simulation import SimulationResult


async def test_filling(
    runner: SimulationTestRunner, simulation_inputs: DhwSimulationInputs
):
    simulation_inputs_no_consumption = simulation_inputs.model_copy(
        update={
            "dhw_hotwater_demand": simulation_inputs.dhw_hotwater_demand.model_copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    runner._simulation.update_simulation_inputs(simulation_inputs_no_consumption)  # type: ignore

    result = runner.run(60)

    assert isinstance(runner._control, DhwControl)
    assert runner._control._dhw_drives_flow_controller.enabled()
    assert runner._control._dhw_dc_flow_controller.enabled()

    assert isinstance(result, SimulationResult)
    assert result.sensor_values.dhw_flow_drives.flow.value > 0.1
    assert result.sensor_values.dhw_flow_dc.flow.value > 0.1

    simulation_inputs_no_drives = simulation_inputs.model_copy(
        update={
            "dhw_drives_supply": simulation_inputs.dhw_drives_supply.model_copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    runner._simulation.update_simulation_inputs(simulation_inputs_no_drives)  # type: ignore

    result = runner.run(180)

    assert isinstance(runner._control, DhwControl)
    assert not runner._control._dhw_drives_flow_controller.enabled()
    assert runner._control._dhw_dc_flow_controller.enabled()

    assert isinstance(result, SimulationResult)
    assert result.sensor_values.dhw_flow_drives.flow.value == approx(0.0, abs=0.01)
    assert result.sensor_values.dhw_flow_dc.flow.value > 0.1

    # wait for tanks to fill
    result = runner.run(1000)

    assert isinstance(result, SimulationResult)
    assert isinstance(runner._control, DhwControl) and isinstance(
        runner._control._tanks_controller, TanksController
    )
    assert not runner._control._tanks_controller.filling
    assert not runner._control._dhw_drives_flow_controller.enabled()
    assert not runner._control._dhw_dc_flow_controller.enabled()

    assert result.sensor_values.dhw_flow_drives.flow.value == approx(0.0, abs=0.01)
    assert result.sensor_values.dhw_flow_dc.flow.value == approx(0.0, abs=0.01)
    assert (
        result.sensor_values.dhw_level_tank1.level.value
        > runner._control.parameters.minimum_tank_level
    )
    assert (
        result.sensor_values.dhw_level_tank2.level.value
        > runner._control.parameters.minimum_tank_level
    )
    assert (
        result.sensor_values.dhw_level_tank3.level.value
        > runner._control.parameters.minimum_tank_level
    )


def test_boosting_transitions(
    runner: SimulationTestRunner, simulation_inputs: DhwSimulationInputs
):
    # all tanks full and ht available
    runner._control.update_parameters(
        runner._control.parameters.model_copy(update={"maximum_tank_level": 10})
    )

    result = runner.run(120)

    assert isinstance(runner._control, DhwControl) and isinstance(
        runner._control._tanks_controller, TanksController
    )
    assert runner._control._tanks_controller.boosting
    assert runner._control.mode.is_boosting_high_temperature
    assert isinstance(result, SimulationResult)
    assert result.sensor_values.dhw_flow_boosting.flow.value > 0.1
    assert (
        result.sensor_values.dhw_temperature_boosting_supply.temperature.value
        < result.sensor_values.dhw_temperature_boosting_return.temperature.value
    )

    # filling and no ht available (switch to heat pump)
    simulation_inputs_no_ht = simulation_inputs.model_copy(
        update={
            "dhw_ht_supply": simulation_inputs.dhw_ht_supply.model_copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    runner._simulation.update_simulation_inputs(simulation_inputs_no_ht)  # type: ignore
    result = runner.run(120)

    assert runner._control._tanks_controller.boosting
    assert runner._control.mode.is_boosting_heatpump
    assert isinstance(result, SimulationResult)
    assert result.sensor_values.dhw_flow_boosting.flow.value == approx(25, abs=0.2)
    assert (
        result.sensor_values.dhw_temperature_boosting_supply.temperature.value
        < result.sensor_values.dhw_temperature_boosting_return.temperature.value
    )

    # all tanks at temperature
    runner._control.update_parameters(
        runner._control.parameters.copy(update={"maximum_tank_temperature": 10})
    )
    result = runner.run(120)

    assert not runner._control._tanks_controller.boosting
    assert runner._control.mode.is_boosting_idle
    assert isinstance(result, SimulationResult)
    assert result.sensor_values.dhw_flow_boosting.flow.value == approx(0.0, abs=0.1)
