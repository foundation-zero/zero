from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError
from pytest import approx

from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.controllers import PcmChargeController
from thrs.control.modules.pcm import PcmControl, PcmControlMode, PcmParameters
from thrs.input_output.definitions.controllers import PcmChargeStatus, PcmChargingState
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation

type PcmSimulation = Simulation[
    PcmSensorValues,
    PcmControlValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
]


class _Clock:
    def __init__(self, start: datetime) -> None:
        self._now = start

    def __call__(self) -> datetime:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += timedelta(seconds=seconds)


_SWITCH_VALVES = (
    "pcm_switch_charging_return",
    "pcm_switch_discharging",
    "pcm_switch_charging_supply",
    "pcm_switch_consumers",
)


def _set_charge_status(
    controller: PcmChargeController,
    charge_status: PcmChargeStatus,
    charging_state: PcmChargingState = PcmChargingState.IDLE,
) -> None:
    """Force a charge controller's reported state, bypassing anchoring."""
    controller._charge_status = charge_status
    controller._charging_state = charging_state


def _settle_valves(control: PcmControl, sensor_values: PcmSensorValues) -> None:
    """Make the switch valve feedback match whatever is currently commanded."""
    for name in _SWITCH_VALVES:
        setpoint = getattr(control._current_values, name).setpoint.value
        getattr(sensor_values, name).position_rel.value = setpoint


def _new_control(
    parameters: PcmParameters | None = None,
) -> tuple[PcmControl, _Clock]:
    clock = _Clock(datetime(2026, 1, 1, tzinfo=UTC))
    control = PcmControl(
        parameters or PcmParameters(), clock, MachineStateLoggingServiceNoop()
    )
    return control, clock


def _hot_settled_sensor_values(control: PcmControl) -> PcmSensorValues:
    """Sensor values with valves settled at idle and a hot producers return."""
    sensor_values = PcmSensorValues.zero()
    sensor_values.pcm_temperature_producers_return.temperature.value = 70.0
    _settle_valves(control, sensor_values)
    return sensor_values


def _all_modules(control: PcmControl) -> tuple[PcmChargeController, ...]:
    return (
        control.module1_charge_controller,
        control.module2_charge_controller,
        control.module3_charge_controller,
        control.module4_charge_controller,
    )


# -- state machine (FMU-free, deterministic under a manual clock) -----------------


def test_idle_when_nothing_requested():
    control, _clock = _new_control()
    sensor_values = _hot_settled_sensor_values(control)

    control.control(sensor_values)

    assert control.mode == PcmControlMode(mode="idle")


def test_charging_request_waits_for_valves_to_settle():
    control, _clock = _new_control()
    control.parameters.charging_requested = True
    sensor_values = PcmSensorValues.zero()
    sensor_values.pcm_temperature_producers_return.temperature.value = 70.0
    # Valves are still at their zero() default, not the idle setpoint.

    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="idle")

    _settle_valves(control, sensor_values)
    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="charging")


def test_charging_exits_to_idle_when_all_modules_are_full():
    control, _clock = _new_control()
    control.parameters.charging_requested = True
    sensor_values = _hot_settled_sensor_values(control)

    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="charging")

    for charge_controller in _all_modules(control):
        _set_charge_status(charge_controller, PcmChargeStatus.FULL)
    control.control(sensor_values)

    assert control.mode == PcmControlMode(mode="idle")


def test_full_modules_get_no_flow_while_charging():
    control, _clock = _new_control()
    control.parameters.charging_requested = True
    sensor_values = _hot_settled_sensor_values(control)

    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="charging")

    _set_charge_status(control.module1_charge_controller, PcmChargeStatus.FULL)
    control.control(sensor_values)

    setpoints = control._flow_balance_controller.get_setpoints()
    actives = control._flow_balance_controller.get_active_valves()
    assert setpoints[0] == 0.0
    assert actives[0] is False
    assert setpoints[1:] == [control.parameters.pcm_charge_flow] * 3
    assert actives[1:] == [True, True, True]


def test_supplying_includes_unknown_modules():
    control, _clock = _new_control()
    control.parameters.supplying_requested = True
    sensor_values = PcmSensorValues.zero()
    _settle_valves(control, sensor_values)

    control.control(sensor_values)

    assert control.mode == PcmControlMode(mode="supplying")
    assert control._flow_balance_controller.get_active_valves() == [True] * 4
    assert (
        control._flow_balance_controller.get_setpoints()
        == [control.parameters.pcm_discharge_flow] * 4
    )


def test_empty_modules_are_excluded_from_supplying():
    control, _clock = _new_control()
    control.parameters.supplying_requested = True
    sensor_values = PcmSensorValues.zero()
    _settle_valves(control, sensor_values)

    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="supplying")

    _set_charge_status(control.module1_charge_controller, PcmChargeStatus.EMPTY)
    _set_charge_status(control.module2_charge_controller, PcmChargeStatus.EMPTY)
    control.control(sensor_values)

    setpoints = control._flow_balance_controller.get_setpoints()
    actives = control._flow_balance_controller.get_active_valves()
    assert setpoints[:2] == [0.0, 0.0]
    assert actives[:2] == [False, False]
    assert setpoints[2:] == [control.parameters.pcm_discharge_flow] * 2
    assert actives[2:] == [True, True]


def test_supplying_exits_to_idle_when_all_modules_are_empty():
    control, _clock = _new_control()
    control.parameters.supplying_requested = True
    sensor_values = PcmSensorValues.zero()
    _settle_valves(control, sensor_values)

    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="supplying")

    for charge_controller in _all_modules(control):
        _set_charge_status(charge_controller, PcmChargeStatus.EMPTY)
    control.control(sensor_values)

    assert control.mode == PcmControlMode(mode="idle")


def test_stalled_module_is_dropped_after_grace_and_stall_elapse():
    control, clock = _new_control(
        PcmParameters(grace_period=10, stall_duration=10, retry_delay=50)
    )
    control.parameters.charging_requested = True
    sensor_values = _hot_settled_sensor_values(control)

    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="charging")

    # Modules 2-4 keep reading CHARGING; module 1 never does, so it stalls out.
    for charge_controller in (
        control.module2_charge_controller,
        control.module3_charge_controller,
        control.module4_charge_controller,
    ):
        _set_charge_status(
            charge_controller, PcmChargeStatus.UNKNOWN, PcmChargingState.CHARGING
        )

    clock.advance(
        control.parameters.grace_period + control.parameters.stall_duration + 1
    )
    control.control(sensor_values)

    assert control.mode == PcmControlMode(mode="charging")
    assert control._dropped_modules == {control.module1_charge_controller}
    setpoints = control._flow_balance_controller.get_setpoints()
    assert setpoints[0] == 0.0
    assert setpoints[1:] == [control.parameters.pcm_charge_flow] * 3


def test_charging_retry_lockout_after_all_modules_stall():
    control, clock = _new_control(
        PcmParameters(grace_period=10, stall_duration=10, retry_delay=50)
    )
    control.parameters.charging_requested = True
    sensor_values = _hot_settled_sensor_values(control)

    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="charging")

    # No module ever reads CHARGING: all stall out once grace + stall elapse.
    clock.advance(
        control.parameters.grace_period + control.parameters.stall_duration + 1
    )
    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="idle")
    assert control._charging_retry_until is not None

    # Modules are still eligible, but the lockout must keep charging from resuming.
    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="idle")

    clock.advance(control.parameters.retry_delay + 1)
    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="charging")


def test_full_modules_are_not_dropped_and_leave_no_lockout():
    control, clock = _new_control(
        PcmParameters(grace_period=10, stall_duration=10, retry_delay=50)
    )
    control.parameters.charging_requested = True
    sensor_values = _hot_settled_sensor_values(control)
    _set_charge_status(control.module1_charge_controller, PcmChargeStatus.FULL)

    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="charging")

    for charge_controller in _all_modules(control)[1:]:
        _set_charge_status(
            charge_controller, PcmChargeStatus.UNKNOWN, PcmChargingState.CHARGING
        )

    clock.advance(
        control.parameters.grace_period + control.parameters.stall_duration + 1
    )
    control.control(sensor_values)
    assert control._dropped_modules == set()

    for charge_controller in _all_modules(control):
        _set_charge_status(charge_controller, PcmChargeStatus.FULL)
    control.control(sensor_values)

    assert control.mode == PcmControlMode(mode="idle")
    assert control._charging_retry_until is None


def test_charging_and_supplying_never_switch_directly():
    control, _clock = _new_control()
    control.parameters.charging_requested = True
    sensor_values = _hot_settled_sensor_values(control)

    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="charging")
    _settle_valves(control, sensor_values)  # switch valves finish traveling

    control.parameters.charging_requested = False
    control.parameters.supplying_requested = True
    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="idle")  # left charging first

    control.control(sensor_values)
    assert control.mode == PcmControlMode(
        mode="idle"
    )  # waiting for valves to reach idle

    _settle_valves(control, sensor_values)  # valves finish traveling to idle
    control.control(sensor_values)
    assert control.mode == PcmControlMode(mode="supplying")


# -- parameters ---------------------------------------------------------------


def test_charging_and_supplying_cannot_both_be_requested():
    with pytest.raises(ValidationError):
        PcmParameters(charging_requested=True, supplying_requested=True)


def test_minimum_charging_temperature_must_allow_anchoring_full():
    PcmParameters(pcm_charge_flow=2, minimum_charging_temperature=65)

    with pytest.raises(ValidationError):
        PcmParameters(pcm_charge_flow=1, minimum_charging_temperature=65)


# -- FMU-backed sanity checks ---------------------------------------------------


def test_idle_with_real_simulation(control: PcmControl, simulation: PcmSimulation):
    result = simulation.tick(control.initial()[0])

    for _i in range(100):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    pcm_flow = (
        result.sensor_values.pcm_flow_module1.flow.value
        + result.sensor_values.pcm_flow_module2.flow.value
        + result.sensor_values.pcm_flow_module3.flow.value
        + result.sensor_values.pcm_flow_module4.flow.value
    )
    assert control.mode == PcmControlMode(mode="idle")
    assert pcm_flow == approx(0.0, abs=0.1)


def test_module_inlet_follows_the_switches(
    control: PcmControl, simulation: PcmSimulation
):
    """The inlet is the producers header while charging, the consumers mix otherwise."""
    result = simulation.tick(control.control(PcmSensorValues.zero())[0])

    control.parameters.supplying_requested = True
    control.to_supplying(result.sensor_values)  # type: ignore

    for _i in range(100):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert result.sensor_values.consumers_flow_dhw.flow.value == approx(
        result.simulation_outputs.pcm_consumers_return.flow.value  # type: ignore
    )

    consumers_return = result.simulation_inputs.pcm_consumers_supply.temperature.value  # type: ignore
    assert result.sensor_values.pcm_temperature_consumers_return.temperature.value == (
        approx(consumers_return)
    )
    assert result.sensor_values.pcm_heat_module1.temperature_supply.value == approx(
        consumers_return
    )

    control.parameters.supplying_requested = False
    control.parameters.charging_requested = True
    control.to_charging(result.sensor_values)  # type: ignore

    for _i in range(100):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert result.sensor_values.pcm_heat_module1.temperature_supply.value == approx(
        result.sensor_values.pcm_temperature_producers_return.temperature.value
    )
