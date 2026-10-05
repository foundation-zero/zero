from collections.abc import Callable
from datetime import timedelta

import pytest
from pydantic import ValidationError
from pytest import approx

from tests.modules.pcm.conftest import PcmRunner
from thrs.control.modules.pcm import (
    PcmControl,
    PcmControllerState,
    PcmParameters,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Valve
from thrs.input_output.definitions.controllers import (
    PcmChargeControllerValues,
    PcmChargeStatus,
    PcmChargingState,
    PidControllerValues,
)
from thrs.input_output.definitions.simulation import Boundary, TemperatureBoundary
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
)

type Check = Callable[[PcmSensorValues, PcmControlValues, PcmControllerState], None]


def _request(control: PcmControl, **requests: bool) -> None:
    control.update_parameters(
        PcmParameters.model_validate(control.parameters.model_dump() | requests)
    )


def _with_freshwater_draw(
    simulation_inputs: PcmSimulationInputs,
) -> PcmSimulationInputs:
    return simulation_inputs.model_copy(
        update={
            "pcm_freshwater_supply": Boundary(
                temperature=Stamped.stamp(10), flow=Stamped.stamp(10)
            )
        }
    )


def _with_consumers_return(
    simulation_inputs: PcmSimulationInputs, temperature: float
) -> PcmSimulationInputs:
    return simulation_inputs.model_copy(
        update={
            "pcm_consumers_supply": TemperatureBoundary(
                temperature=Stamped.stamp(temperature)
            )
        }
    )


def _with_producers_temperature(
    simulation_inputs: PcmSimulationInputs, temperature: float
) -> PcmSimulationInputs:
    return simulation_inputs.model_copy(
        update={
            "pcm_thrusters_supply": simulation_inputs.pcm_thrusters_supply.model_copy(
                update={"temperature": Stamped.stamp(temperature)}
            ),
            "pcm_pvt_supply": simulation_inputs.pcm_pvt_supply.model_copy(
                update={"temperature": Stamped.stamp(temperature)}
            ),
        }
    )


def _module_flows(sensor_values: PcmSensorValues) -> list[float]:
    return [
        sensor_values.pcm_flow_module1.flow.value,
        sensor_values.pcm_flow_module2.flow.value,
        sensor_values.pcm_flow_module3.flow.value,
        sensor_values.pcm_flow_module4.flow.value,
    ]


def _switch_positions(sensor_values: PcmSensorValues) -> list[float]:
    return [
        sensor_values.pcm_switch_charging_return.position_rel.value,
        sensor_values.pcm_switch_discharging.position_rel.value,
        sensor_values.pcm_switch_charging_supply.position_rel.value,
        sensor_values.pcm_switch_consumers.position_rel.value,
    ]


def _switch_setpoints(control_values: PcmControlValues) -> list[float]:
    return [
        control_values.pcm_switch_charging_return.setpoint.value,
        control_values.pcm_switch_discharging.setpoint.value,
        control_values.pcm_switch_charging_supply.setpoint.value,
        control_values.pcm_switch_consumers.setpoint.value,
    ]


def _charge_controllers(
    controller_state: PcmControllerState,
) -> list[PcmChargeControllerValues]:
    return [
        controller_state.module1_charge_controller,
        controller_state.module2_charge_controller,
        controller_state.module3_charge_controller,
        controller_state.module4_charge_controller,
    ]


def _flow_controllers(
    controller_state: PcmControllerState,
) -> list[PidControllerValues]:
    return [
        controller_state.module1_flow_controller,
        controller_state.module2_flow_controller,
        controller_state.module3_flow_controller,
        controller_state.module4_flow_controller,
    ]


def _all_modules(controller_state: PcmControllerState, status: PcmChargeStatus) -> bool:
    return all(
        PcmChargeStatus(charge_controller.charge_status.value) is status
        for charge_controller in _charge_controllers(controller_state)
    )


def _modules_get_flow_until(
    exhausted: PcmChargeStatus, flow: float, in_mode: Callable[[], bool]
) -> Check:
    """Checks that a module gets `flow` until it reports `exhausted`, and none after."""
    previous_statuses: list[PcmChargeStatus] = []

    def check(_, __, controller_state: PcmControllerState) -> None:
        if in_mode() and previous_statuses:
            for status, flow_controller in zip(
                previous_statuses, _flow_controllers(controller_state), strict=True
            ):
                is_exhausted = status is exhausted
                assert flow_controller.enabled.value is not is_exhausted
                assert flow_controller.setpoint.value == (0 if is_exhausted else flow)
        previous_statuses[:] = [
            PcmChargeStatus(charge_controller.charge_status.value)
            for charge_controller in _charge_controllers(controller_state)
        ]

    return check


def _charge(runner: PcmRunner, control: PcmControl) -> None:
    _request(control, charging_requested=True)
    runner.run_until(lambda *_: control.mode.is_charging, within=timedelta(minutes=2))
    runner.run_until(lambda *_: control.mode.is_idle, within=timedelta(minutes=40))
    _request(control, charging_requested=False)


def test_idle_when_nothing_requested(runner: PcmRunner):
    for sensor_values, control_values, controller_state in runner.ticks_for(
        timedelta(minutes=2)
    ):
        assert not control_values.pcm_pump.on.value
        assert not any(
            flow_controller.enabled.value
            for flow_controller in _flow_controllers(controller_state)
        )
        assert _module_flows(sensor_values) == approx([0] * 4, abs=0.1)

    assert runner.mode_transitions(lambda mode: mode.mode) == ["idle"]


def test_charging_until_all_modules_are_full(runner: PcmRunner, control: PcmControl):
    _request(control, charging_requested=True)
    check_flows = _modules_get_flow_until(
        PcmChargeStatus.FULL,
        control.parameters.pcm_charge_flow,
        lambda: control.mode.is_charging,
    )

    def check_charging(sensor_values, control_values, controller_state) -> None:
        check_flows(sensor_values, control_values, controller_state)
        if control.mode.is_charging:
            assert not control_values.pcm_pump.on.value
            assert _switch_setpoints(control_values) == [
                Valve.OPEN,
                Valve.CLOSED,
                Valve.OPEN,
                Valve.OPEN,
            ]

    runner.run_until(lambda *_: control.mode.is_charging, within=timedelta(minutes=2))
    runner.run_until(
        lambda *_: control.mode.is_idle,
        within=timedelta(minutes=40),
        check=check_charging,
    )

    for _, _, controller_state in runner.ticks_for(timedelta(minutes=2)):
        assert control.mode.is_idle
        assert _all_modules(controller_state, PcmChargeStatus.FULL)
    sensor_values, *_ = runner.tick()

    assert _module_flows(sensor_values) == approx([0] * 4, abs=0.1)
    assert runner.mode_transitions(lambda mode: mode.mode) == [
        "idle",
        "charging",
        "idle",
    ]


def test_no_charging_below_minimum_charging_temperature(
    runner: PcmRunner,
    control: PcmControl,
    simulation_inputs: PcmSimulationInputs,
):
    producers_temperature = control.parameters.minimum_charging_temperature - 5
    runner.update_simulation_inputs(
        _with_producers_temperature(simulation_inputs, producers_temperature)
    )
    _request(control, charging_requested=True)

    for _ in runner.ticks_for(timedelta(minutes=5)):
        assert control.mode.is_idle
    sensor_values, *_ = runner.tick()

    assert sensor_values.pcm_temperature_producers_return.temperature.value == approx(
        producers_temperature, abs=1
    )


def test_charging_resumes_without_lockout_once_a_full_module_loses_heat(
    runner: PcmRunner,
    control: PcmControl,
    simulation_inputs: PcmSimulationInputs,
):
    _charge(runner, control)
    _request(control, charging_requested=True)

    runner.update_simulation_inputs(_with_freshwater_draw(simulation_inputs))
    runner.run_until(
        lambda *_: control.mode.is_charging,
        within=timedelta(seconds=control.parameters.retry_delay / 2),
    )

    assert runner.mode_transitions(lambda mode: mode.mode) == [
        "idle",
        "charging",
        "idle",
        "charging",
    ]


def test_stalled_module_is_dropped_and_charging_retried_after_lockout(
    runner: PcmRunner,
    control: PcmControl,
    simulation_inputs: PcmSimulationInputs,
):
    # The freshwater draw keeps module 1 from charging.
    runner.update_simulation_inputs(_with_freshwater_draw(simulation_inputs))
    _request(control, charging_requested=True)
    parameters = control.parameters
    stall_after = timedelta(seconds=parameters.grace_period + parameters.stall_duration)

    runner.run_until(lambda *_: control.mode.is_charging, within=timedelta(minutes=2))
    for _, _, controller_state in runner.ticks_for(stall_after - timedelta(seconds=5)):
        assert controller_state.module1_flow_controller.enabled.value
    _, _, controller_state = runner.run_until(
        lambda _, __, controller_state: (
            not controller_state.module1_flow_controller.enabled.value
        ),
        within=timedelta(seconds=10),
    )

    assert control.mode.is_charging
    assert [
        flow_controller.enabled.value
        for flow_controller in _flow_controllers(controller_state)
    ] == [False, True, True, True]
    assert controller_state.module1_flow_controller.setpoint.value == 0

    runner.run_until(lambda *_: control.mode.is_idle, within=timedelta(minutes=30))
    for _ in runner.ticks_for(
        timedelta(seconds=parameters.retry_delay) - timedelta(seconds=5)
    ):
        assert control.mode.is_idle
    runner.run_until(lambda *_: control.mode.is_charging, within=timedelta(seconds=10))

    assert runner.mode_transitions(lambda mode: mode.mode) == [
        "idle",
        "charging",
        "idle",
        "charging",
    ]


def test_closed_modules_carry_no_flow_while_charging(
    runner: PcmRunner,
    control: PcmControl,
    simulation_inputs: PcmSimulationInputs,
):
    # The freshwater draw keeps module 1 from charging, so it stalls out of the first
    # charge. Modules 2-4 fill up, and the retry charges module 1 on its own.
    runner.update_simulation_inputs(_with_freshwater_draw(simulation_inputs))
    _request(control, charging_requested=True)

    def only_module1_active(_, __, controller_state: PcmControllerState) -> bool:
        return control.mode.is_charging and [
            flow_controller.enabled.value
            for flow_controller in _flow_controllers(controller_state)
        ] == [True, False, False, False]

    def only_module1_flows(sensor_values: PcmSensorValues, *_) -> bool:
        return _module_flows(sensor_values) == approx(
            [control.parameters.pcm_charge_flow, 0, 0, 0], abs=0.5
        )

    runner.run_until(only_module1_active, within=timedelta(minutes=40))
    runner.run_until_stable(
        only_module1_flows,
        stable_for=timedelta(seconds=30),
        within=timedelta(minutes=3),
    )


def test_supplying_from_charged_modules(
    runner: PcmRunner,
    control: PcmControl,
    simulation_inputs: PcmSimulationInputs,
):
    _charge(runner, control)
    runner.update_simulation_inputs(_with_consumers_return(simulation_inputs, 45))
    _request(control, supplying_requested=True)
    discharge_flow = control.parameters.pcm_discharge_flow

    def check_supplying(_, control_values, controller_state) -> None:
        if control.mode.is_supplying:
            assert control_values.pcm_pump.on.value
            assert _switch_setpoints(control_values) == [
                Valve.CLOSED,
                Valve.OPEN,
                Valve.CLOSED,
                Valve.OPEN,
            ]
            assert [
                flow_controller.setpoint.value
                for flow_controller in _flow_controllers(controller_state)
            ] == [discharge_flow] * 4

    def all_modules_discharging(sensor_values, _, controller_state) -> bool:
        return _module_flows(sensor_values) == approx(
            [discharge_flow] * 4, abs=0.5
        ) and all(
            PcmChargingState(charge_controller.charging_state.value)
            is PcmChargingState.DISCHARGING
            for charge_controller in _charge_controllers(controller_state)
        )

    runner.run_until(
        lambda *_: control.mode.is_supplying,
        within=timedelta(minutes=5),
        check=check_supplying,
    )
    runner.run_until_stable(
        all_modules_discharging,
        stable_for=timedelta(minutes=1),
        within=timedelta(minutes=10),
    )

    assert runner.mode_transitions(lambda mode: mode.mode) == [
        "idle",
        "charging",
        "idle",
        "supplying",
    ]


def test_supplying_until_all_modules_are_empty(
    runner: PcmRunner,
    control: PcmControl,
    simulation_inputs: PcmSimulationInputs,
):
    runner.update_simulation_inputs(_with_consumers_return(simulation_inputs, 15))
    # A high discharge flow empties the modules in well under an hour.
    control.update_parameters(
        PcmParameters(supplying_requested=True, pcm_discharge_flow=15)
    )

    runner.run_until(lambda *_: control.mode.is_supplying, within=timedelta(minutes=2))
    runner.run_until(
        lambda *_: control.mode.is_idle,
        within=timedelta(minutes=60),
        check=_modules_get_flow_until(
            PcmChargeStatus.EMPTY,
            control.parameters.pcm_discharge_flow,
            lambda: control.mode.is_supplying,
        ),
    )

    for _, control_values, controller_state in runner.ticks_for(timedelta(minutes=2)):
        assert control.mode.is_idle
        assert not control_values.pcm_pump.on.value
        assert _all_modules(controller_state, PcmChargeStatus.EMPTY)
    assert runner.mode_transitions(lambda mode: mode.mode) == [
        "idle",
        "supplying",
        "idle",
    ]


def test_supplying_stalls_when_the_modules_do_not_discharge(
    runner: PcmRunner, control: PcmControl
):
    # The consumers return is warmer than the PCM, so the modules charge instead.
    _request(control, supplying_requested=True)
    parameters = control.parameters
    stall_after = timedelta(seconds=parameters.grace_period + parameters.stall_duration)

    runner.run_until(lambda *_: control.mode.is_supplying, within=timedelta(minutes=2))
    for _ in runner.ticks_for(stall_after - timedelta(seconds=5)):
        assert control.mode.is_supplying
    runner.run_until(lambda *_: control.mode.is_idle, within=timedelta(seconds=10))
    for _ in runner.ticks_for(
        timedelta(seconds=parameters.retry_delay) - timedelta(seconds=5)
    ):
        assert control.mode.is_idle
    runner.run_until(lambda *_: control.mode.is_supplying, within=timedelta(seconds=10))

    assert runner.mode_transitions(lambda mode: mode.mode) == [
        "idle",
        "supplying",
        "idle",
        "supplying",
    ]


def test_switching_between_charging_and_supplying_waits_in_idle(
    runner: PcmRunner, control: PcmControl
):
    idle_switch_setpoints = [Valve.CLOSED, Valve.CLOSED, Valve.CLOSED, Valve.OPEN]
    _request(control, charging_requested=True)
    runner.run_until(lambda *_: control.mode.is_charging, within=timedelta(minutes=2))
    runner.run(60)

    _request(control, charging_requested=False, supplying_requested=True)
    sensor_values, *_ = runner.run_until(
        lambda *_: control.mode.is_supplying, within=timedelta(minutes=5)
    )

    assert _switch_positions(sensor_values) == approx(idle_switch_setpoints, abs=0.05)
    assert runner.mode_transitions(lambda mode: mode.mode) == [
        "idle",
        "charging",
        "idle",
        "supplying",
    ]


def test_module_inlet_follows_the_switches(
    runner: PcmRunner,
    control: PcmControl,
    simulation_inputs: PcmSimulationInputs,
):
    """The inlet is the producers header while charging, the consumers mix otherwise."""
    consumers_return = simulation_inputs.pcm_consumers_supply.temperature.value

    def inlet_at_consumers_return(sensor_values: PcmSensorValues, *_) -> bool:
        return sensor_values.pcm_heat_module1.temperature_supply.value == approx(
            consumers_return, abs=0.5
        )

    def inlet_at_producers_return(sensor_values: PcmSensorValues, *_) -> bool:
        return sensor_values.pcm_heat_module1.temperature_supply.value == approx(
            sensor_values.pcm_temperature_producers_return.temperature.value, abs=0.5
        )

    _request(control, supplying_requested=True)
    runner.run_until(lambda *_: control.mode.is_supplying, within=timedelta(minutes=2))
    sensor_values, *_ = runner.run_until_stable(
        inlet_at_consumers_return,
        stable_for=timedelta(seconds=30),
        within=timedelta(minutes=3),
    )

    simulation_outputs = runner.simulation_outputs
    assert simulation_outputs is not None
    assert sensor_values.consumers_flow_dhw.flow.value == approx(
        simulation_outputs.pcm_consumers_return.flow.value
    )
    assert sensor_values.pcm_temperature_consumers_return.temperature.value == approx(
        consumers_return
    )

    _request(control, supplying_requested=False, charging_requested=True)
    runner.run_until(lambda *_: control.mode.is_charging, within=timedelta(minutes=5))
    runner.run_until_stable(
        inlet_at_producers_return,
        stable_for=timedelta(seconds=30),
        within=timedelta(minutes=3),
    )


def test_charging_and_supplying_cannot_both_be_requested():
    with pytest.raises(ValidationError):
        PcmParameters(charging_requested=True, supplying_requested=True)


def test_minimum_charging_temperature_must_allow_anchoring_full():
    PcmParameters(pcm_charge_flow=2, minimum_charging_temperature=65)

    with pytest.raises(ValidationError):
        PcmParameters(pcm_charge_flow=1, minimum_charging_temperature=65)
