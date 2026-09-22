from datetime import datetime, timedelta

import pytest
from pytest import approx

from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.control.modules.dhw import (
    DhwControl,
    DhwParameters,
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

    assert not control._drives_flow_controller.enabled()
    assert control._dc_flow_controller.enabled()

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
        control.parameters.model_copy(
            update={
                "minimum_tank_level": 2,
                "maximum_tank_level": 10,
                "full_level_lower_band": 5,
            }
        )
    )

    sensor_values, *_ = runner.run(150)

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
    assert sensor_values.dhw_flow_boosting.flow.value == approx(25, abs=0.5)
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
            update={
                "minimum_tank_level": 2,
                "maximum_tank_level": 10,
                "full_level_lower_band": 5,
                "ht_boosting_enabled": False,
            }
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
        control.parameters.model_copy(
            update={
                "minimum_tank_level": 2,
                "maximum_tank_level": 10,
                "full_level_lower_band": 5,
            }
        )
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
                "minimum_tank_level": 2,
                "maximum_tank_level": 10,
                "full_level_lower_band": 5,
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
        control.parameters.model_copy(
            update={
                "minimum_tank_level": 2,
                "maximum_tank_level": 10,
                "full_level_lower_band": 5,
            }
        )
    )

    # run up to the tick the machine commits to boosting
    runner.run_until(
        lambda sensor_values, control_values, controller_state: control.mode.is_boosting
    )

    # while the boosting valves travel the pump must not be driven
    while not control._boosting_loop_open(runner.tick()[0]):  # type: ignore
        assert control._current_values.dhw_pump.dutypoint.value == 0.1
        assert not control._pump_temperature_controller.enabled()

    sensor_values, *_ = runner.run(120)

    assert sensor_values is not None
    assert control._pump_temperature_controller.enabled()
    assert sensor_values.dhw_flow_boosting.flow.value > 0.1


def test_pump_minimum_dutypoint_follows_parameters(parameters: DhwParameters):
    control = DhwControl(parameters, datetime.now)
    pumps = (
        control._pump_flow_controller,
        control._pump_temperature_controller,
    )

    for pump in pumps:
        pump(None)
        assert pump._output_limits == (0.1, 1.0)

    control.update_parameters(
        parameters.model_copy(update={"minimum_pump_dutypoint": 0.4})
    )
    for pump in pumps:
        pump(None)
        assert pump._output_limits == (0.4, 1.0)


def test_minimum_pump_dutypoint_rejects_below_pump_floor(
    parameters: DhwParameters,
):
    with pytest.raises(ValueError, match=r"greater than or equal to 0\.1"):
        DhwParameters(**{**parameters.model_dump(), "minimum_pump_dutypoint": 0.05})


def test_reset_restores_initial_control_state(
    control: DhwControl, parameters, sensor_values: DhwSensorValues
):
    state_logger = control.state_logger

    # Dirty all mutable state: tick once, then force the rest.
    control.control(sensor_values)
    control._current_values.dhw_pump.dutypoint = Stamped.stamp(0.9)
    for pid in (
        control._drives_flow_controller,
        control._dc_flow_controller,
        control._pump_temperature_controller,
    ):
        if not pid.enabled():
            pid.enable()
    control._pump_temperature_controller(control._pump_temperature_controller.setpoint)
    control._state_machine.set_state("boosting_heatpump")
    control._tanks_controller._filling_tank = control._tanks_controller._tanks[0]
    control._boosting_entered_at = datetime.now()
    control._boosting_shortfall_since = datetime.now()
    control._heatpump_stall_cooldown_until = datetime.now()

    control.reset()

    # Parameters, time function and logger are kept (same objects, no re-log).
    assert control.parameters is parameters
    assert control.state_logger is state_logger
    # State machine is back at its initial state without firing transitions.
    assert control.mode == control.initial_mode
    assert control.mode.is_boosting_idle
    # Current controls are back at initial values.
    assert control._current_values.dhw_pump.dutypoint.value == approx(0.1)
    assert control._current_values.dhw_pump.on.value is False
    assert control._current_values.dhw_heatpump.on.value is False
    assert control._current_values.dhw_flowcontrol_drives.setpoint.value == approx(0.0)
    assert control._current_values.dhw_flowcontrol_dc.setpoint.value == approx(0.0)
    # Sub-controllers are fresh: PIDs disabled with no integral state, pump
    # selection cleared, tanks controller rebound to the new control values.
    assert not control._drives_flow_controller.enabled()
    assert not control._dc_flow_controller.enabled()
    assert not control._pump_temperature_controller.enabled()
    assert not control._pump_flow_controller.enabled()
    assert control._boosting_pump_controller is None
    assert control._boosting_pump_measurement is None
    assert control._boosting_entered_at is None
    assert control._boosting_shortfall_since is None
    assert control._heatpump_stall_cooldown_until is None
    assert not control._tanks_controller.filling
    assert not control._tanks_controller.boosting
    assert (
        control._tanks_controller._tanks[0]._inlet
        is control._current_values.dhw_switch_tank1_inlet
    )
    assert (
        control._current_controller_state.dhw_tanks_controller.tank1_state.value
        == TankState.NEEDS_FILL.value
    )


class _Clock:
    def __init__(self, start: datetime):
        self._now = start

    def __call__(self) -> datetime:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += timedelta(seconds=seconds)


def _drive_heatpump_boosting_heat(
    sensor_values: DhwSensorValues, flow: float, delta: float
):
    # Open only the heatpump source valve so the computed dhw_heatpump heat is
    # non-zero. The heatpump heats the return, so heat into the tank is positive
    # when boosting_return exceeds boosting_supply.
    sensor_values.dhw_switch_heatpump.position_rel.value = 1.0
    sensor_values.dhw_switch_high_temperature.position_rel.value = 0.0
    sensor_values.dhw_switch_low_temperature.position_rel.value = 0.0
    sensor_values.dhw_flow_boosting.flow.value = flow
    sensor_values.dhw_temperature_boosting_supply.temperature.value = 45.0
    sensor_values.dhw_temperature_boosting_return.temperature.value = 45.0 + delta


def test_boosting_stall_grace_suppresses_check(parameters: DhwParameters):
    clock = _Clock(datetime(2026, 1, 1))
    control = DhwControl(parameters, clock)
    sensor_values = DhwSensorValues.zero()  # heatpump heat reads zero (valves shut)
    control._state_machine.set_state("boosting_heatpump")
    control._boosting_entered_at = clock()

    # No heat transfer, but still inside the startup grace -> not stalled.
    clock.advance(parameters.boosting_startup_grace - 1)
    assert not control._boosting_stalled(sensor_values, "boosting_heatpump")
    assert control._boosting_shortfall_since is None


def test_boosting_stall_trips_after_window_and_sets_heatpump_cooldown(
    parameters: DhwParameters,
):
    clock = _Clock(datetime(2026, 1, 1))
    control = DhwControl(parameters, clock)
    sensor_values = DhwSensorValues.zero()
    control._state_machine.set_state("boosting_heatpump")
    control._boosting_entered_at = clock()

    clock.advance(parameters.boosting_startup_grace + 1)
    # First shortfall observation after grace starts the debounce timer.
    assert not control._boosting_stalled(sensor_values, "boosting_heatpump")
    assert control._boosting_shortfall_since is not None

    clock.advance(parameters.boosting_stall_window / 2)
    assert not control._boosting_stalled(sensor_values, "boosting_heatpump")

    clock.advance(parameters.boosting_stall_window)
    assert control._boosting_stalled(sensor_values, "boosting_heatpump")
    assert control._boosting_shortfall_since is None
    assert control._heatpump_stall_cooldown_until == clock() + timedelta(
        seconds=parameters.boosting_stall_cooldown
    )


def test_boosting_stall_debounce_resets_on_recovery(parameters: DhwParameters):
    clock = _Clock(datetime(2026, 1, 1))
    control = DhwControl(parameters, clock)
    sensor_values = DhwSensorValues.zero()
    control._state_machine.set_state("boosting_heatpump")
    control._boosting_entered_at = clock()
    clock.advance(parameters.boosting_startup_grace + 1)

    # Shortfall builds partway through the window...
    assert not control._boosting_stalled(sensor_values, "boosting_heatpump")
    clock.advance(parameters.boosting_stall_window / 2)
    assert not control._boosting_stalled(sensor_values, "boosting_heatpump")

    # ...then heat recovers, resetting the debounce.
    _drive_heatpump_boosting_heat(sensor_values, flow=25, delta=5)
    assert not control._boosting_stalled(sensor_values, "boosting_heatpump")
    assert control._boosting_shortfall_since is None

    # A fresh shortfall must run the full window again, not the leftover.
    recovered = DhwSensorValues.zero()
    assert not control._boosting_stalled(recovered, "boosting_heatpump")
    clock.advance(parameters.boosting_stall_window / 2)
    assert not control._boosting_stalled(recovered, "boosting_heatpump")
    clock.advance(parameters.boosting_stall_window)
    assert control._boosting_stalled(recovered, "boosting_heatpump")


def test_boosting_stall_high_temperature_does_not_set_cooldown(
    parameters: DhwParameters,
):
    clock = _Clock(datetime(2026, 1, 1))
    control = DhwControl(parameters, clock)
    sensor_values = DhwSensorValues.zero()
    control._state_machine.set_state("boosting_high_temperature")
    control._boosting_entered_at = clock()
    clock.advance(parameters.boosting_startup_grace + 1)

    assert not control._boosting_stalled(sensor_values, "boosting_high_temperature")
    clock.advance(parameters.boosting_stall_window / 2)
    assert not control._boosting_stalled(sensor_values, "boosting_high_temperature")
    clock.advance(parameters.boosting_stall_window)
    assert control._boosting_stalled(sensor_values, "boosting_high_temperature")
    # HT re-enters via its primary-side gate, so it takes no cooldown.
    assert control._heatpump_stall_cooldown_until is None


def test_heatpump_boosting_unavailable_during_cooldown(parameters: DhwParameters):
    clock = _Clock(datetime(2026, 1, 1))
    control = DhwControl(parameters, clock)
    sensor_values = DhwSensorValues.zero()
    control._tanks_controller._boost_candidate = control._tanks_controller._tanks[0]
    _drive_heatpump_boosting_heat(sensor_values, flow=25, delta=5)
    control._heatpump_stall_cooldown_until = clock() + timedelta(
        seconds=parameters.boosting_stall_cooldown
    )

    # Demand and heat are fine, but a live cooldown blocks the heatpump.
    assert not control._heatpump_boosting_available(sensor_values)

    clock.advance(parameters.boosting_stall_cooldown + 1)
    assert control._heatpump_boosting_available(sensor_values)
    assert control._heatpump_stall_cooldown_until is None


def test_control_loop_aborts_stalled_heatpump_boost(parameters: DhwParameters):
    clock = _Clock(datetime(2026, 1, 1))
    fast = parameters.model_copy(
        update={
            "ht_boosting_enabled": False,
            "heatpump_boosting_enabled": True,
            "boosting_startup_grace": 3,
            "boosting_stall_window": 3,
            "boosting_stall_cooldown": 100,
        }
    )
    control = DhwControl(fast, clock)
    sensor_values = DhwSensorValues.zero()
    # tank1 hot+full (kept in use), tank2 full+cold (boosts), tank3 empty. The
    # boosting loop sensor valves stay shut, so heat transfer reads zero.
    sensor_values.dhw_temperature_tank1.temperature.value = 60
    sensor_values.dhw_temperature_tank2.temperature.value = 20
    sensor_values.dhw_temperature_tank3.temperature.value = 0
    sensor_values.dhw_level_tank1.level.value = 250
    sensor_values.dhw_level_tank2.level.value = 250
    sensor_values.dhw_level_tank3.level.value = 10

    modes = []
    for _ in range(20):
        control.control(sensor_values)
        modes.append(control.mode.boosting_mode)
        clock.advance(1)

    assert "boosting_heatpump" in modes  # it did start boosting the cold tank
    assert control.mode.is_boosting_idle  # and gave up once it stalled
    assert control._heatpump_stall_cooldown_until is not None
    assert control._current_values.dhw_switch_heatpump.setpoint.value == 0.0


def test_boosting_stall_window_rejects_negative(parameters: DhwParameters):
    with pytest.raises(ValueError, match=r"greater than or equal to 0"):
        DhwParameters(**{**parameters.model_dump(), "boosting_stall_window": -1})
