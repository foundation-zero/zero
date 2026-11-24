from collections.abc import Callable
from datetime import datetime
from typing import Literal, NoReturn

from transitions import Machine, State

from thrs.classes.control import Control
from thrs.control.controllers import FlowBalanceController, PidController
from thrs.control.modules.thrusters.io import (
    ThrustersControlValues,
    ThrustersSensorValues,
)
from thrs.control.modules.thrusters.state import (
    ThrustersControllerState,
    ThrustersControlMode,
    ThrustersParameters,
)
from thrs.input_output.alarms import BaseAlarms, Severity, alarm
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.units import Celsius, LMin, PcsMode, Ratio
from thrs.orchestration.module import ModuleDescription

RECOVERY_MIX_UPPER_BOUND: Ratio = 0.2
RECOVERY_MIX_LOWER_BOUND: Ratio = 0.05


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> ThrustersControlValues:  # noqa: N802
    return ThrustersControlValues(
        thrusters_pump1=Pump(
            dutypoint=Stamped(value=0.1, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        thrusters_pump2=Pump(
            dutypoint=Stamped(value=0.1, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        thrusters_mix_recovery=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        thrusters_mix_exchanger=Valve(
            setpoint=Stamped(
                value=Valve.MIXING_A_TO_AB,
                timestamp=timestamp,
            )
        ),
        thrusters_flowcontrol_aft=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        thrusters_flowcontrol_fwd=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        thrusters_switch_recovery=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        thrusters_switch_aft=Valve(
            setpoint=Stamped(value=Valve.SWITCH_B, timestamp=timestamp)
        ),
        thrusters_switch_fwd=Valve(
            setpoint=Stamped(value=Valve.SWITCH_B, timestamp=timestamp)
        ),
    )


def _INITIAL_CONTROLLER_STATE(timestamp: datetime) -> ThrustersControllerState:  # noqa: N802
    return ThrustersControllerState(
        thrusters_heat_dump_controller=PidController.zero(timestamp),
        thrusters_warmup_mix_controller=PidController.zero(timestamp),
        thrusters_pump_controller=PidController.zero(timestamp),
        thrusters_aft_recovery_temperature_controller=PidController.zero(timestamp),
        thrusters_fwd_recovery_temperature_controller=PidController.zero(timestamp),
        thrusters_aft_flow_controller=PidController.zero(timestamp),
        thrusters_fwd_flow_controller=PidController.zero(timestamp),
        parameters=ThrustersParameters(),
        control_mode=None,
    )


class ThrustersControl(
    Control[
        ThrustersSensorValues,
        ThrustersControlValues,
        ThrustersParameters,
        ThrustersControlMode,
        ThrustersControllerState,
    ]
):
    _state_machine: Machine
    _transitions: list[dict]
    _states: list[State]
    _parameters: ThrustersParameters

    state: str  # Value set by Machine transitions logic

    def __init__(
        self,
        parameters: ThrustersParameters,
        time_fn: Callable[[], datetime],
    ) -> None:
        self._parameters = parameters
        self._time: Callable[[], datetime] = time_fn
        self._current_control_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )

        self._init_state_machine_states()
        self._init_state_machine_transitions()
        self._state_machine = Machine(
            self, transitions=self._transitions, states=self._states, initial="idle"
        )
        self._init_controllers(parameters)

    def _init_controllers(self, parameters):
        if not hasattr(self, "_state_machine") or self._state_machine is None:
            raise ValueError(
                "State machine must be initialized before creating control methods"
            )

        """Create controllers and control methods for the different thrusters control aspects."""
        self._heat_dump_controller = PidController[Ratio, Celsius](
            self._current_control_values.thrusters_mix_exchanger.setpoint.value,
            lambda: (
                self._parameters.maximum_supply_temperature
                if self.mode.is_warmup or self.mode.is_recovery
                else self._parameters.cooling_temperature
            ),
            lambda: self._parameters.heat_dump_tuning,
            self._time,
        )
        self._warmup_mix_controller = PidController[Ratio, Celsius](
            self._current_control_values.thrusters_mix_recovery.setpoint.value,
            lambda: self._parameters.warmup_temperature,
            lambda: self._parameters.warmup_mix_tuning,
            self._time,
        )
        self._pump_controller = PidController[Ratio, LMin](
            self._current_control_values.thrusters_pump1.dutypoint.value,
            0,  # Gets overridden by flow balance controller
            lambda: self._parameters.pump_tuning,
            self._time,
            output_limits=(0.1, 1),
        )

        self._aft_recovery_temperature_controller = PidController[LMin, Celsius](
            parameters.thrusters_minimum_flow,
            lambda: self._parameters.recovery_temperature,
            lambda: self._parameters.aft_temperature_tuning,
            self._time,
            lambda: (
                self._parameters.thrusters_minimum_flow,
                self._parameters.thrusters_maximum_flow,
            ),
        )

        self._fwd_recovery_temperature_controller = PidController[LMin, Celsius](
            parameters.thrusters_minimum_flow,
            lambda: self._parameters.recovery_temperature,
            lambda: self._parameters.fwd_temperature_tuning,
            self._time,
            lambda: (
                self._parameters.thrusters_minimum_flow,
                self._parameters.thrusters_maximum_flow,
            ),
        )

        self._aft_flow_controller = PidController[Ratio, LMin](
            self._current_control_values.thrusters_flowcontrol_aft.setpoint.value,
            0,  # Gets overridden by flow balance controller
            lambda: self._parameters.aft_flow_balance_tuning,
            self._time,
        )

        self._fwd_flow_controller = PidController[Ratio, LMin](
            self._current_control_values.thrusters_flowcontrol_fwd.setpoint.value,
            0,  # Gets overridden by flow balance controller
            lambda: self._parameters.fwd_flow_balance_tuning,
            self._time,
        )

        self._most_recently_active_pump: Literal["pump1", "pump2"] | None = None
        self._active_pump: Pump | None = None

        self._flow_balance_controller = FlowBalanceController(
            [
                self._current_control_values.thrusters_flowcontrol_aft,
                self._current_control_values.thrusters_flowcontrol_fwd,
            ],
            [self._aft_flow_controller, self._fwd_flow_controller],
            self._active_pump,
            self._pump_controller,
            self._time,
        )

    def _init_state_machine_transitions(self):
        """Define the transitions between states, their triggers and conditions."""
        self._transitions = [
            {
                "trigger": "_check_overheat",
                "source": ["idle", "warmup", "recovery", "cooldown", "cooling"],
                "dest": "cooling",
                "conditions": self._is_overheating,
            },
            {
                "trigger": "_check_pcs_mode",
                "source": ["cooling"],
                "dest": None,
                "conditions": lambda sensor_values: (
                    False
                ),  # stay in cooling until manually changed
            },
            {
                "trigger": "_check_pcs_mode",
                "source": ["idle", "cooldown"],
                "dest": "warmup",
                "conditions": self._pcs_propulsion_hydrogeneration,
            },
            {
                "trigger": "_check_pcs_mode",
                "source": ["idle", "warmup", "recovery", "cooldown"],
                "dest": "cooling",
                "conditions": self._pcs_maneuvering,
            },
            {
                "trigger": "_check_pcs_mode",
                "source": ["warmup", "recovery", "cooling"],
                "dest": "cooldown",
                "conditions": self._pcs_off,
            },
            {
                "trigger": "_check_pcs_mode",
                "source": ["cooldown"],
                "dest": "idle",
                "conditions": [self._cooled_down, self._pcs_off],
            },
            {
                "trigger": "_check_warmup_mix",
                "source": "warmup",
                "dest": "recovery",
                "conditions": self._warmup_mix_open,
            },
            {
                "trigger": "_check_warmup_mix",
                "source": "recovery",
                "dest": "warmup",
                "conditions": self._warmup_mix_closed,
            },
        ]

    def _init_state_machine_states(self):
        """Define the states and their entry/exit actions."""
        self._states = [
            State(
                name="idle",
                on_enter=[
                    self._deactivate_pump,
                    self._disable_flow_balancing,
                    self._set_valves_to_recovery,
                    self._disable_heat_dump,
                    self._open_flowcontrol_valves,
                    self._stop_warmup_mix,
                ],
                on_exit=[
                    self._activate_pump,
                    self._enable_flow_balancing,
                    self._enable_heat_dump,
                ],
            ),
            State(
                name="warmup",
                on_enter=[
                    self._set_valves_to_recovery,
                    self._enable_warmup_mix,
                ],
            ),
            State(
                name="recovery",
                on_enter=[
                    self._set_valves_to_recovery,
                    self._enable_warmup_mix,
                    self._enable_recovery_temperature_controllers,
                ],
                on_exit=[
                    self._disable_recovery_temperature_controllers,
                ],
            ),
            State(
                name="cooling",
                on_enter=[
                    self._stop_warmup_mix,
                    self._set_valves_to_cooling,
                    self._set_cooling_flow_setpoints,
                ],
            ),
            State(
                name="cooldown",
                on_enter=[
                    self._stop_warmup_mix,
                    self._set_cooldown_flow_setpoints,
                ],
            ),
        ]

    @property
    def parameters(self) -> ThrustersParameters:
        return self._parameters

    def update_parameters(self, parameters: ThrustersParameters):
        self._parameters = parameters

    @property
    def mode(self) -> ThrustersControlMode:
        mode: str = self.state
        return ThrustersControlMode(mode=mode)

    def initial(self) -> tuple[ThrustersControlValues, ThrustersControllerState]:
        return (
            _INITIAL_CONTROL_VALUES(self._time()),
            _INITIAL_CONTROLLER_STATE(self._time()),
        )

    def reset(self) -> None:
        self._current_control_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )
        self._state_machine.set_state(self._state_machine.initial)  # pyrefly: ignore[bad-argument-type]
        self._init_controllers(self._parameters)

    def control(
        self, sensor_values: ThrustersSensorValues
    ) -> tuple[ThrustersControlValues, ThrustersControllerState]:
        self._check_pcs_mode(sensor_values)  # pyrefly: ignore[missing-attribute]
        self._check_overheat(sensor_values)  # pyrefly: ignore[missing-attribute]
        self._control_heat_dump(sensor_values)

        # Recovery controls
        if self.mode.is_warmup or self.mode.is_recovery:
            self._control_warmup_mix(sensor_values)
            self._check_warmup_mix(sensor_values)  # pyrefly: ignore[missing-attribute]
        if self.mode.is_warmup:
            self._set_warmup_flow_setpoints(sensor_values)
        if self.mode.is_recovery:
            self._set_recovery_flow_setpoints(sensor_values)

        # Basic controls
        self._control_flow_balance(sensor_values)

        controller_state = ThrustersControllerState(
            thrusters_heat_dump_controller=self._heat_dump_controller.values(),
            thrusters_warmup_mix_controller=self._warmup_mix_controller.values(),
            thrusters_pump_controller=self._pump_controller.values(),
            thrusters_aft_recovery_temperature_controller=self._aft_recovery_temperature_controller.values(),
            thrusters_fwd_recovery_temperature_controller=self._fwd_recovery_temperature_controller.values(),
            thrusters_aft_flow_controller=self._aft_flow_controller.values(),
            thrusters_fwd_flow_controller=self._fwd_flow_controller.values(),
            parameters=self._parameters,
            control_mode=self.mode,
        )

        return (self._current_control_values, controller_state)

    def _is_overheating(self, sensor_values: ThrustersSensorValues):
        return (
            sensor_values.thrusters_temperature_supply.temperature.value is not None
            and sensor_values.thrusters_temperature_supply.temperature.value > 90
        )

    def _cooled_down(self, sensor_values: ThrustersSensorValues):
        return (
            max(
                sensor_values.thrusters_temperature_fwd.temperature.value
                if sensor_values.thrusters_flow_fwd.flow.value > 1e-2
                else 0,
                sensor_values.thrusters_temperature_aft.temperature.value
                if sensor_values.thrusters_flow_aft.flow.value > 1e-2
                else 0,
            )
            < self._parameters.cooling_temperature
        )

    def _set_valves_to_cooling(self, sensor_values: ThrustersSensorValues):
        self._current_control_values.thrusters_switch_aft.setpoint = Stamped(
            value=Valve.SWITCH_A, timestamp=self._time()
        )
        self._current_control_values.thrusters_switch_fwd.setpoint = Stamped(
            value=Valve.SWITCH_A, timestamp=self._time()
        )
        self._current_control_values.thrusters_switch_recovery.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )

    def _set_valves_to_recovery(self, sensor_values: ThrustersSensorValues):
        self._current_control_values.thrusters_switch_aft.setpoint = Stamped(
            value=Valve.SWITCH_B, timestamp=self._time()
        )
        self._current_control_values.thrusters_switch_fwd.setpoint = Stamped(
            value=Valve.SWITCH_B, timestamp=self._time()
        )
        self._current_control_values.thrusters_switch_recovery.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )

    def _enable_flow_balancing(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.enable(
            [
                sensor_values.thrusters_thruster_aft.active.value,
                sensor_values.thrusters_thruster_fwd.active.value,
            ]
        )

    def _open_flowcontrol_valves(self, sensor_values: ThrustersSensorValues):
        self._current_control_values.thrusters_flowcontrol_aft.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )
        self._current_control_values.thrusters_flowcontrol_fwd.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )

    def _disable_flow_balancing(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.disable()

    def _enable_recovery_temperature_controllers(
        self, sensor_values: ThrustersSensorValues
    ):
        self._aft_recovery_temperature_controller.enable()
        self._fwd_recovery_temperature_controller.enable()

    def _disable_recovery_temperature_controllers(
        self, sensor_values: ThrustersSensorValues
    ):
        self._aft_recovery_temperature_controller.disable()
        self._fwd_recovery_temperature_controller.disable()

    def _enable_warmup_mix(self, sensor_values: ThrustersSensorValues):
        if not self._warmup_mix_controller.enabled():
            self._warmup_mix_controller.enable()

    def _stop_warmup_mix(self, sensor_values: ThrustersSensorValues):
        if self._warmup_mix_controller.enabled():
            self._warmup_mix_controller.disable()
        self._current_control_values.thrusters_mix_recovery.setpoint = Stamped(
            value=Valve.MIXING_B_TO_AB, timestamp=self._time()
        )

    def _warmup_mix_open(self, sensor_values: ThrustersSensorValues):
        return (
            self._current_control_values.thrusters_mix_recovery.setpoint.value
            > RECOVERY_MIX_UPPER_BOUND
        )

    def _warmup_mix_closed(self, sensor_values: ThrustersSensorValues):
        return (
            self._current_control_values.thrusters_mix_recovery.setpoint.value
            < RECOVERY_MIX_LOWER_BOUND
        )

    def _set_recovery_temperature(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_setpoint(
            self._parameters.recovery_temperature
        )

    def _set_cooling_flow(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_setpoint(self._parameters.cooling_flow)

    def _enable_heat_dump(self, sensor_values: ThrustersSensorValues):
        self._heat_dump_controller.enable()

    def _disable_heat_dump(self, sensor_values: ThrustersSensorValues):
        self._heat_dump_controller.disable()

    def _control_warmup_mix(self, sensor_values: ThrustersSensorValues):
        self._current_control_values.thrusters_mix_recovery.setpoint = Stamped(
            value=(
                self._warmup_mix_controller(
                    sensor_values.thrusters_temperature_recovery.temperature.value,
                )
            ),
            timestamp=self._time(),
        )

    def _control_heat_dump(self, sensor_values: ThrustersSensorValues):
        if self._heat_dump_controller.enabled():
            self._current_control_values.thrusters_mix_exchanger.setpoint = Stamped(
                value=(
                    self._heat_dump_controller(
                        sensor_values.thrusters_temperature_supply.temperature.value,
                    )
                ),
                timestamp=self._time(),
            )

    def _set_recovery_flow_setpoints(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_active_valves(
            [
                sensor_values.thrusters_thruster_aft.active.value,
                sensor_values.thrusters_thruster_fwd.active.value,
            ]
        )

        flow_setpoints = [
            self._aft_recovery_temperature_controller(
                sensor_values.thrusters_temperature_aft.temperature.value,
            )
            if sensor_values.thrusters_thruster_aft.active.value
            else 0,
            self._fwd_recovery_temperature_controller(
                sensor_values.thrusters_temperature_fwd.temperature.value,
            )
            if sensor_values.thrusters_thruster_fwd.active.value
            else 0,
        ]

        self._flow_balance_controller.set_setpoints(flow_setpoints)

    def _set_warmup_flow_setpoints(self, sensor_values: ThrustersSensorValues):
        actives = [
            sensor_values.thrusters_thruster_aft.active.value,
            sensor_values.thrusters_thruster_fwd.active.value,
        ]
        self._flow_balance_controller.set_active_valves(actives)
        self._flow_balance_controller.set_setpoints(
            [
                self._parameters.thrusters_minimum_flow if active else 0
                for active in actives
            ]
        )

    def _set_cooling_flow_setpoints(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_active_valves(
            [
                sensor_values.thrusters_thruster_aft.active.value,
                sensor_values.thrusters_thruster_fwd.active.value,
            ]
        )
        self._flow_balance_controller.set_setpoint(self._parameters.cooling_flow)

    def _set_cooldown_flow_setpoints(self, sensor_values: ThrustersSensorValues):
        # cool only the last used thrusters by not updating active valves
        self._flow_balance_controller.set_setpoint(self._parameters.cooling_flow)

    def _control_flow_balance(self, sensor_values: ThrustersSensorValues):
        if self._flow_balance_controller.enabled:
            self._flow_balance_controller.set_pump(self._active_pump)
            self._flow_balance_controller(
                [
                    sensor_values.thrusters_flow_aft.flow.value,
                    sensor_values.thrusters_flow_fwd.flow.value,
                ]
            )

    def _pcs_off(self, sensor_values: ThrustersSensorValues):
        return sensor_values.thrusters_pcs.mode.value == PcsMode.OFF.value

    def _pcs_maneuvering(self, sensor_values: ThrustersSensorValues):
        return sensor_values.thrusters_pcs.mode.value == PcsMode.MANEUVERING.value

    def _pcs_propulsion_hydrogeneration(self, sensor_values: ThrustersSensorValues):
        return sensor_values.thrusters_pcs.mode.value in {
            PcsMode.PROPULSION.value,
            PcsMode.REGENERATION.value,
        }

    def _activate_pump(self, sensor_values: ThrustersSensorValues):
        if self._active_pump:
            self._raise_warning("A pump was already active upon selecting")
        elif self._most_recently_active_pump == "pump1":
            self._most_recently_active_pump = "pump2"
            self._active_pump = self._current_control_values.thrusters_pump2
        else:
            self._most_recently_active_pump = "pump1"
            self._active_pump = self._current_control_values.thrusters_pump1

        self._active_pump.on = Stamped(value=True, timestamp=self._time())

    def _deactivate_pump(self, sensor_values: ThrustersSensorValues):
        if not self._active_pump:
            self._raise_warning("No pump active when deactivating")

        self._active_pump.on = Stamped(value=False, timestamp=self._time())
        self._active_pump = None

    def _raise_warning(self, message: str) -> NoReturn:
        raise Warning(message)


class ThrustersAlarms(BaseAlarms):
    @alarm("Overheating alarm", severity=Severity.ALARM)
    def check_overheating(
        self,
        sensor_values: ThrustersSensorValues,
        control_values: ThrustersControlValues,
        controller_state: ThrustersControllerState,
    ) -> str | None:
        if sensor_values.thrusters_temperature_supply.temperature.value > 95:
            return "Thrusters supply temperature above 95 °C"
        return None


THRUSTERS_MODULE_DESCRIPTION = ModuleDescription(
    ThrustersSensorValues,
    ThrustersControlValues,
    ThrustersParameters,
    ThrustersControl,
    ThrustersControllerState,
    ThrustersAlarms,
)
