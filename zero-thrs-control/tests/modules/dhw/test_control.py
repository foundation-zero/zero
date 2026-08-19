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
    runner.update_simulation_inputs(simulation_inputs_no_consumption)

    sensor_values, _control_values, controller_state = runner.run(30)

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
    runner.update_simulation_inputs(simulation_inputs_no_drives)

    sensor_values, _control_values, controller_state = runner.run(60)

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
    runner.update_simulation_inputs(simulation_inputs_no_consumption)

    # run until tank1 start filling
    sensor_values, *_ = runner.run_until(
        lambda sensor_values, control_values, controller_state: (
            controller_state.dhw_tanks_controller.tank1_state.value
            == TankState.FILLING.value
        )
    )

    # run until tank1 is full
    sensor_values, *_ = runner.run_until(
        lambda sensor_values, control_values, controller_state: (
            controller_state.dhw_tanks_controller.tank1_state.value
            != TankState.FILLING.value
        )
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
    runner.update_simulation_inputs(simulation_inputs_no_ht)
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
        control.parameters.model_copy(
            update={"minimum_tank_temperature": 10, "maximum_tank_temperature": 10}
        )
    )
    sensor_values, *_ = runner.run(120)

    assert not control._tanks_controller.boosting
    assert control.mode.is_boosting_idle
    assert isinstance(sensor_values, DhwSensorValues)
    assert sensor_values.dhw_flow_boosting.flow.value == approx(0.0, abs=0.1)


def test_boosting_falls_back_to_heatpump_when_ht_disabled(
    control: DhwControl,
    runner: SimulationTestRunner,
    simulation: Simulation,
    simulation_inputs: DhwSimulationInputs,
):
    # all tanks full and ht available, but ht boosting is not permitted
    control.update_parameters(
        control.parameters.model_copy(
            update={"maximum_tank_level": 10, "ht_boosting_enabled": False}
        )
    )

    sensor_values, *_ = runner.run(240)

    assert control._tanks_controller.boosting
    assert control.mode.is_boosting_heatpump
    assert isinstance(sensor_values, DhwSensorValues)
    assert sensor_values.dhw_flow_boosting.flow.value == approx(25, abs=0.2)

    # permitting ht boosting again hands boosting back to the preferred source
    control.update_parameters(
        control.parameters.model_copy(update={"ht_boosting_enabled": True})
    )
    sensor_values, *_ = runner.run(120)

    assert control.mode.is_boosting_high_temperature


def test_boosting_stays_idle_when_all_sources_disabled(
    control: DhwControl,
    runner: SimulationTestRunner,
    simulation: Simulation,
    simulation_inputs: DhwSimulationInputs,
):
    # all tanks full and ht available, so boosting starts from high temperature
    control.update_parameters(
        control.parameters.model_copy(update={"maximum_tank_level": 10})
    )
    runner.run(120)

    assert control.mode.is_boosting_high_temperature

    control.update_parameters(
        control.parameters.model_copy(
            update={"ht_boosting_enabled": False, "heatpump_boosting_enabled": False}
        )
    )

    # the machine must settle in idle and not flip-flop back into a boosting mode
    modes = []
    _, control_values, _ = runner.tick()
    for _ in range(120):
        _, control_values, _ = runner.tick()
        modes.append(control.mode.boosting_mode)

    assert all(mode == "idle" for mode in modes)

    # demand persists, but the tank controller may no longer act on it
    assert control._tanks_controller.boost_demand
    assert not control._tanks_controller.boosting
    assert all(
        valve.setpoint.value == 0.0
        for valve in [
            control_values.dhw_switch_tank1_boosting_supply,
            control_values.dhw_switch_tank1_boosting_return,
            control_values.dhw_switch_tank2_boosting_supply,
            control_values.dhw_switch_tank2_boosting_return,
            control_values.dhw_switch_tank3_boosting_supply,
            control_values.dhw_switch_tank3_boosting_return,
        ]
    )


def test_boosting_tank_reports_needs_boost_while_unauthorised(
    control: DhwControl,
    runner: SimulationTestRunner,
    simulation: Simulation,
    simulation_inputs: DhwSimulationInputs,
):
    # tanks fill up and need a boost, but no source is permitted to supply it
    control.update_parameters(
        control.parameters.model_copy(
            update={
                "maximum_tank_level": 10,
                "ht_boosting_enabled": False,
                "heatpump_boosting_enabled": False,
            }
        )
    )

    _, _, controller_state = runner.run(120)

    assert control.mode.is_boosting_idle
    assert control._tanks_controller.boost_demand
    assert TankState.NEEDS_BOOST.value in [
        controller_state.dhw_tanks_controller.tank1_state.value,
        controller_state.dhw_tanks_controller.tank2_state.value,
        controller_state.dhw_tanks_controller.tank3_state.value,
    ]
    assert TankState.BOOSTING.value not in [
        controller_state.dhw_tanks_controller.tank1_state.value,
        controller_state.dhw_tanks_controller.tank2_state.value,
        controller_state.dhw_tanks_controller.tank3_state.value,
    ]


def test_boosting_pump_held_until_boosting_loop_open(
    control: DhwControl,
    runner: SimulationTestRunner,
    simulation: Simulation,
    simulation_inputs: DhwSimulationInputs,
):
    control.update_parameters(
        control.parameters.model_copy(update={"maximum_tank_level": 10})
    )

    # run up to the tick the machine commits to boosting
    runner.run_until(
        lambda sensor_values, control_values, controller_state: control.mode.is_boosting
    )

    # while the boosting valves travel the pump must not be driven
    while not control._boosting_loop_open(runner.tick()[0]):  # type: ignore
        assert control._current_values.dhw_pump.dutypoint.value == 0.0
        assert not control._pump_temperature_controller.enabled()

    sensor_values, *_ = runner.run(120)

    assert sensor_values is not None
    assert control._pump_temperature_controller.enabled()
    assert sensor_values.dhw_flow_boosting.flow.value > 0.1
