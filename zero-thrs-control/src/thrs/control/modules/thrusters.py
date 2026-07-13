from datetime import datetime
from typing import Callable, Literal, NoReturn

from pydantic import model_validator
from transitions import Machine, State

from thrs.classes.control import Control, ControlMode
from thrs.classes.machine_state_logger import (
    MachineStateLoggingServiceNoop,
    StateLogger,
)
from thrs.control.controllers import FlowBalanceController, PidController
from thrs.db.models.machine_state import (
    MachineStateEvent,
)
from thrs.input_output.alarms import BaseAlarms, Severity, alarm
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.units import Celsius, LMin, PcsMode, Ratio, Tuning
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
)
from thrs.orchestration.module import ModuleDescription


class ThrustersControlMode(ControlMode):
    mode: str

    @property
    def is_idle(self) -> bool:
        return self.mode == "idle"

    @property
    def is_recovery(self) -> bool:
        return self.mode == "recovery"


class ThrustersControllerState(ThrsValues):
    pass


class ThrustersParameters(ThrsValues):
    maximum_supply_temperature: Celsius = 75
    cooling_temperature: Celsius = 38
    cooling_flow: LMin = 25
    recovery_temperature: Celsius = 65
    warmup_temperature: Celsius = 60
    thrusters_minimum_flow: LMin = 5
    thrusters_maximum_flow: LMin = 30
    pump_tuning: Tuning = (0.01, 0.001, 0)
    warmup_mix_tuning: Tuning = (-0.05, -0.001, 0)
    heat_dump_tuning: Tuning = (0.05, 0.01, 0)
    aft_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    fwd_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    aft_temperature_tuning: Tuning = (-0.01, -0.001, 0)
    fwd_temperature_tuning: Tuning = (-0.01, -0.001, 0)

    @model_validator(mode="after")
    def check_temperature_setpoints(self):
        if self.maximum_supply_temperature < self.recovery_temperature:
            raise ValueError(
                "Maximum recovery temperature must be greater than recovery temperature"
            )
        if self.recovery_temperature < self.warmup_temperature:
            raise ValueError(
                "Recovery temperature must be greater than warmup temperature"
            )
        if self.warmup_temperature < self.cooling_temperature:
            raise ValueError(
                "Warmup temperature must be greater than cooling temperature"
            )
        return self


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> ThrustersControlValues:
    return ThrustersControlValues(
        thrusters_pump1=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        thrusters_pump2=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
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
            setpoint=Stamped(value=Valve.SWITCH_BRANCH, timestamp=timestamp)
        ),
        thrusters_switch_fwd=Valve(
            setpoint=Stamped(value=Valve.SWITCH_BRANCH, timestamp=timestamp)
        ),
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
    _parameters: "ThrustersParameters"

    # Log state machine attributes
    state_logger: "StateLogger"
    state: str  # Value set by Machine transitions logic

    def __init__(
        self,
        parameters: ThrustersParameters,
        time_fn: Callable[[], datetime],
        state_logger: StateLogger | None = None,
    ) -> None:
        self._parameters = parameters
        self._time: Callable[[], datetime] = time_fn
        self.state_logger = state_logger or MachineStateLoggingServiceNoop()
        self._current_control_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )

        # State machine setup
        self._init_state_machine_states()
        self._init_state_machine_transitions()
        self._state_machine = self.state_logger.create_logged_state_machine(
            self, transitions=self._transitions, states=self._states, initial="idle"
        )
        self._init_controllers(parameters)

        # Log configuration
        self.state_logger.log_parameters_initial_state(parameters)

    def _init_controllers(self, parameters):
        if not hasattr(self, "_state_machine") or self._state_machine is None:
            raise ValueError(
                "State machine must be initialized before creating control methods"
            )

        """Create controllers and control methods for the different thrusters control aspects."""
        self._heat_dump_controller = PidController[Ratio, Celsius](
            self._current_control_values.thrusters_mix_exchanger.setpoint.value,
            lambda: self._parameters.maximum_supply_temperature
            if self.mode.is_recovery
            else self._parameters.cooling_temperature,
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

        self._most_recently_active_pump: None | Literal["pump1", "pump2"] = None
        self._active_pump: None | Pump = None

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
                "source": ["idle", "recovery", "cooldown", "cooling"],
                "dest": "cooling",
                "conditions": self._is_overheating,
            },
            {
                "trigger": "_check_pcs_mode",
                "source": ["cooling"],
                "dest": None,
                "conditions": lambda sensor_values: False,  # stay in cooling until manually changed
            },
            {
                "trigger": "_check_pcs_mode",
                "source": ["idle", "cooldown"],
                "dest": "recovery",
                "conditions": self._pcs_propulsion_hydrogeneration,
            },
            {
                "trigger": "_check_pcs_mode",
                "source": ["idle", "recovery", "cooldown"],
                "dest": "cooling",
                "conditions": self._pcs_maneuvering,
            },
            {
                "trigger": "_check_pcs_mode",
                "source": ["recovery", "cooling"],
                "dest": "cooldown",
                "conditions": self._pcs_off,
            },
            {
                "trigger": "_check_pcs_mode",
                "source": ["cooldown"],
                "dest": "idle",
                "conditions": [self._cooled_down, self._pcs_off],
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
                ],
                on_exit=[
                    self._activate_pump,
                    self._enable_flow_balancing,
                    self._enable_heat_dump,
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
                    self._disable_warmup_mix,
                    self._disable_recovery_temperature_controllers,
                    self._close_recovery_mix,
                ],
            ),
            State(
                name="cooling",
                on_enter=[
                    self._set_valves_to_cooling,
                    self._set_cooling_flow_setpoints,
                ],
            ),
            State(
                name="cooldown",
                on_enter=[
                    self._set_cooldown_flow_setpoints,
                ],
            ),
        ]

    @property
    def parameters(self) -> ThrustersParameters:
        return self._parameters

    @StateLogger.log_parameters
    def update_parameters(self, parameters: ThrustersParameters):
        self._parameters = parameters

    def modes(self) -> list[str]:
        return list(self._state_machine.states.keys())

    @property
    def initial_mode(self) -> ThrustersControlMode:
        initial_mode: str = self._state_machine.initial  # type: ignore
        return ThrustersControlMode(mode=initial_mode)

    @property
    def mode(self) -> ThrustersControlMode:
        mode: str = self.state  # type: ignore
        return ThrustersControlMode(mode=mode)

    def initial(self) -> tuple[ThrustersControlValues, ThrustersControllerState]:
        return (_INITIAL_CONTROL_VALUES(self._time()), ThrustersControllerState())

    @StateLogger.log_warnings
    def control(
        self, sensor_values: ThrustersSensorValues
    ) -> tuple[ThrustersControlValues, ThrustersControllerState]:
        self._check_pcs_mode(sensor_values)  # type: ignore
        self._check_overheat(sensor_values)  # type: ignore
        self._control_heat_dump(sensor_values)

        # Recovery controls
        if self.mode.is_recovery:
            self._check_overheat(sensor_values)  # type: ignore
            self._set_recovery_flow_setpoints(sensor_values)
            self._control_warmup_mix(sensor_values)

        # Basic controls
        self._control_flow_balance(sensor_values)
        return (self._current_control_values, ThrustersControllerState())

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
            value=Valve.SWITCH_STRAIGHT, timestamp=self._time()
        )
        self._current_control_values.thrusters_switch_fwd.setpoint = Stamped(
            value=Valve.SWITCH_STRAIGHT, timestamp=self._time()
        )
        self._current_control_values.thrusters_switch_recovery.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )

    def _set_valves_to_recovery(self, sensor_values: ThrustersSensorValues):
        self._current_control_values.thrusters_switch_aft.setpoint = Stamped(
            value=Valve.SWITCH_BRANCH, timestamp=self._time()
        )
        self._current_control_values.thrusters_switch_fwd.setpoint = Stamped(
            value=Valve.SWITCH_BRANCH, timestamp=self._time()
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
        self._warmup_mix_controller.enable()

    def _disable_warmup_mix(self, sensor_values: ThrustersSensorValues):
        self._warmup_mix_controller.disable()

    def _close_recovery_mix(self, sensor_values: ThrustersSensorValues):
        self._current_control_values.thrusters_mix_recovery.setpoint = Stamped(
            value=Valve.MIXING_B_TO_AB, timestamp=self._time()
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

    def _set_cooling_flow_setpoints(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_active_valves(
            [
                sensor_values.thrusters_thruster_aft.active.value,
                sensor_values.thrusters_thruster_fwd.active.value,
            ]
        )
        self._flow_balance_controller.set_setpoint(25.0)

    def _set_cooldown_flow_setpoints(self, sensor_values: ThrustersSensorValues):
        # cool only the last used thrusters by not updating active valves
        self._flow_balance_controller.set_setpoint(25.0)

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
            self.raise_warning("A pump was already active upon selecting")
        else:
            if self._most_recently_active_pump == "pump1":
                self._most_recently_active_pump = "pump2"
                self._active_pump = self._current_control_values.thrusters_pump2

            else:
                self._most_recently_active_pump = "pump1"
                self._active_pump = self._current_control_values.thrusters_pump1

            # Example event log
            self.state_logger.log_event(
                MachineStateEvent(
                    control_name=self.__class__.__name__,
                    event_name="pump activated",
                    event_details=self._most_recently_active_pump,
                )
            )
        self._active_pump.on = Stamped(value=True, timestamp=self._time())

    def _deactivate_pump(self, sensor_values: ThrustersSensorValues):
        if not self._active_pump:
            self.raise_warning("No pump active when deactivating")

        self._active_pump.on = Stamped(value=False, timestamp=self._time())
        self._active_pump.dutypoint = Stamped(value=0, timestamp=self._time())
        self._active_pump = None

    def raise_warning(self, message: str) -> NoReturn:
        raise Warning(message)


class ThrustersAlarms(BaseAlarms):
    @alarm("Overheating alarm", severity=Severity.ALARM)
    def check_overheating(
        self,
        sensor_values: ThrustersSensorValues,
        control_values: ThrustersControlValues,
        parameters: ThrustersParameters,
    ) -> str | None:
        if sensor_values.thrusters_temperature_supply.temperature.value > 95:
            return "Thrusters supply temperature above 95 °C"
        return None


THRUSTERS_MODULE_DESCRIPTION = ModuleDescription(
    ThrustersSensorValues,
    ThrustersControlValues,
    ThrustersParameters,
    ThrustersControl,
    ThrustersControlMode,
    ThrustersControllerState,
    ThrustersAlarms,
)
