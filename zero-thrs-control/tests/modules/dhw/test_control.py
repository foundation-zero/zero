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
    DhwSensorValues,
    DhwSimulationInputs,
)
from thrs.orchestration.simulation import Simulation


async def test_filling_flow(
    control: DhwControl,
    runner,
    simulation: Simulation,
    simulation_inputs: DhwSimulationInputs,
):
    # start run with flow through drives and dc, no consumption
    simulation_inputs_no_consumption = simulation_inputs.model_copy(
        update={
            "dhw_hotwater_demand": simulation_inputs.dhw_hotwater_demand.model_copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    simulation.update_simulation_inputs(simulation_inputs_no_consumption)

    sensor_values, control_values, controller_state = runner.run(30)

    # filling flows
    assert controller_state.dhw_drives_flow_controller.enabled
    assert controller_state.dhw_dc_flow_controller.enabled

    assert sensor_values.dhw_flow_drives.flow.value > 0.1
    assert sensor_values.dhw_flow_dc.flow.value > 0.1

    # filling only through drives
    simulation_inputs_no_drives = simulation_inputs.model_copy(
        update={
            "dhw_drives_supply": simulation_inputs.dhw_drives_supply.model_copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    simulation.update_simulation_inputs(simulation_inputs_no_drives)

    sensor_values, control_values, controller_state = runner.run(60)

    assert not control._dhw_drives_flow_controller.enabled()
    assert control._dhw_dc_flow_controller.enabled()

    assert isinstance(sensor_values, DhwSensorValues)
    assert sensor_values.dhw_flow_drives.flow.value == approx(0.0, abs=0.01)
    assert sensor_values.dhw_flow_dc.flow.value > 0.1


@pytest.mark.parametrize("overpressure", [0.1, 0.2, 0.3, 0.5])
def test_filling_level(
    control: DhwControl, runner, simulation: Simulation, simulation_inputs, overpressure
):
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
    simulation.update_simulation_inputs(simulation_inputs_no_consumption)

    # run until tank1 start filling
    sensor_values, *_ = runner.run_until(
        lambda sensor_values,
        control_values,
        controller_state: controller_state.dhw_tanks_controller.tank1_state.value
        == TankState.FILLING.value
    )

    # run until tank1 is full
    sensor_values, *_ = runner.run_until(
        lambda sensor_values,
        control_values,
        controller_state: controller_state.dhw_tanks_controller.tank1_state.value
        != TankState.FILLING.value
    )

    assert sensor_values.dhw_level_tank1.level.value == approx(
        control.parameters.maximum_tank_level, abs=10
    )


def test_boosting_transitions(
    control: DhwControl,
    runner: SimulationTestRunner,
    simulation: Simulation,
    simulation_inputs: DhwSimulationInputs,
):
    # all tanks full and ht available
    control.update_parameters(
        control.parameters.model_copy(update={"maximum_tank_level": 10})
    )

    sensor_values, *_ = runner.run(120)

    assert isinstance(control, DhwControl) and isinstance(
        control._tanks_controller, TanksController
    )
    assert control._tanks_controller.boosting
    assert control.mode.is_boosting_high_temperature
    assert isinstance(sensor_values, DhwSensorValues)
    assert sensor_values.dhw_flow_boosting.flow.value > 0.1
    assert (
        sensor_values.dhw_temperature_boosting_supply.temperature.value
        < sensor_values.dhw_temperature_boosting_return.temperature.value
    )

    # filling and no ht available (switch to heat pump)
    simulation_inputs_no_ht = simulation_inputs.model_copy(
        update={
            "dhw_consumers_supply": simulation_inputs.dhw_consumers_supply.model_copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    simulation.update_simulation_inputs(simulation_inputs_no_ht)
    sensor_values, *_ = runner.run(120)

    assert control._tanks_controller.boosting
    assert control.mode.is_boosting_heatpump
    assert isinstance(sensor_values, DhwSensorValues)
    assert sensor_values.dhw_flow_boosting.flow.value == approx(25, abs=0.2)
    assert (
        sensor_values.dhw_temperature_boosting_supply.temperature.value
        < sensor_values.dhw_temperature_boosting_return.temperature.value
    )

    # all tanks at temperature
    control.update_parameters(
        control.parameters.model_copy(update={"maximum_tank_temperature": 10})
    )
    sensor_values, *_ = runner.run(120)

    assert not control._tanks_controller.boosting
    assert control.mode.is_boosting_idle
    assert isinstance(sensor_values, DhwSensorValues)
    assert sensor_values.dhw_flow_boosting.flow.value == approx(0.0, abs=0.1)
