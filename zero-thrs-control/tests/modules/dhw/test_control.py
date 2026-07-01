import pytest
from pytest import approx

from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.control.modules.dhw import (
    DhwControl,
    TanksController,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.units import TankState
from thrs.input_output.modules.dhw import (
    DhwSimulationInputs,
)
from thrs.orchestration.simulation import SimulationResult


async def test_filling_flow(runner, simulation_inputs):
    # start run with flow through drives and dc, no consumption
    simulation_inputs_no_consumption = simulation_inputs.model_copy(
        update={
            "dhw_hotwater_demand": simulation_inputs.dhw_hotwater_demand.model_copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    runner._simulation.update_simulation_inputs(simulation_inputs_no_consumption)

    result, control_values, controller_state = runner.run(30)

    # filling flows
    assert controller_state.dhw_drives_flow_controller.enabled
    assert controller_state.dhw_dc_flow_controller.enabled

    assert result.sensor_values.dhw_flow_drives.flow.value > 0.1
    assert result.sensor_values.dhw_flow_dc.flow.value > 0.1

    # filling only through drives
    simulation_inputs_no_drives = simulation_inputs.model_copy(
        update={
            "dhw_drives_supply": simulation_inputs.dhw_drives_supply.model_copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    runner._simulation.update_simulation_inputs(simulation_inputs_no_drives)

    result, control_values, controller_state = runner.run(60)

    assert not runner._control._dhw_drives_flow_controller.enabled()
    assert runner._control._dhw_dc_flow_controller.enabled()

    assert isinstance(result, SimulationResult)
    assert result.sensor_values.dhw_flow_drives.flow.value == approx(0.0, abs=0.01)
    assert result.sensor_values.dhw_flow_dc.flow.value > 0.1


@pytest.mark.parametrize("overpressure", [0.1, 0.2, 0.3, 0.5])
def test_filling_level(runner, simulation_inputs, overpressure):
    # start run with flow through drives and dc, no consumption
    simulation_inputs_no_consumption = simulation_inputs.model_copy(
        update={
            "dhw_hotwater_demand": simulation_inputs.dhw_hotwater_demand.model_copy(
                update={"flow": Stamped.stamp(0)}
            ),
            "dhw_freshwater_supply": simulation_inputs.dhw_freshwater_supply.model_copy(
                update={"overpressure": Stamped.stamp(overpressure)}
            ),
        }
    )
    runner._simulation.update_simulation_inputs(simulation_inputs_no_consumption)

    # run until tank1 start filling
    result, *_ = runner.run_until(
        lambda result,
        control_values,
        controller_state: controller_state.dhw_tanks_controller.tank1_state.value
        == TankState.FILLING.value
    )

    # run until tank1 is full
    result, *_ = runner.run_until(
        lambda result,
        control_values,
        controller_state: controller_state.dhw_tanks_controller.tank1_state.value
        != TankState.FILLING.value
    )

    assert result.sensor_values.dhw_level_tank1.level.value == approx(
        runner._control.parameters.maximum_tank_level, abs=10
    )


def test_boosting_transitions(
    runner: SimulationTestRunner, simulation_inputs: DhwSimulationInputs
):
    # all tanks full and ht available
    runner._control.update_parameters(
        runner._control.parameters.model_copy(update={"maximum_tank_level": 10})
    )

    result, _, _ = runner.run(120)

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
    runner._simulation.update_simulation_inputs(simulation_inputs_no_ht)
    result, _, _ = runner.run(120)

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
    result, _, _ = runner.run(120)

    assert not runner._control._tanks_controller.boosting
    assert runner._control.mode.is_boosting_idle
    assert isinstance(result, SimulationResult)
    assert result.sensor_values.dhw_flow_boosting.flow.value == approx(0.0, abs=0.1)
