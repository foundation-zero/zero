from datetime import datetime
from typing import Callable, Literal
from pydantic import model_validator

from transitions import Machine, State

from thrs.control.controllers import Controller, FlowBalanceController
from thrs.input_output.alarms import BaseAlarms, Severity, alarm
from thrs.input_output.base import Stamped, ThrsModel
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
)
from thrs.input_output.definitions.units import Celsius, LMin, PcsMode, Ratio, Tuning
from thrs.classes.control import Control, ControlResult


class ThrustersParameters(ThrsModel):
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


_ZERO_TIME = datetime.fromtimestamp(0)
_INITIAL_CONTROL_VALUES = ThrustersControlValues(
    thrusters_pump_1=Pump(
        dutypoint=Stamped(value=0.0, timestamp=_ZERO_TIME),
        on=Stamped(value=False, timestamp=_ZERO_TIME),
    ),
    thrusters_pump_2=Pump(
        dutypoint=Stamped(value=0.0, timestamp=_ZERO_TIME),
        on=Stamped(value=False, timestamp=_ZERO_TIME),
    ),
    thrusters_mix_recovery=Valve(
        setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=_ZERO_TIME)
    ),
    thrusters_mix_exchanger=Valve(
        setpoint=Stamped(
            value=Valve.MIXING_A_TO_AB,
            timestamp=_ZERO_TIME,
        )
    ),
    thrusters_flowcontrol_aft=Valve(
        setpoint=Stamped(value=Valve.CLOSED, timestamp=_ZERO_TIME)
    ),
    thrusters_flowcontrol_fwd=Valve(
        setpoint=Stamped(value=Valve.CLOSED, timestamp=_ZERO_TIME)
    ),
    thrusters_shutoff_recovery=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    thrusters_switch_aft=Valve(
        setpoint=Stamped(value=Valve.SWITCH_BRANCH, timestamp=_ZERO_TIME)
    ),
    thrusters_switch_fwd=Valve(
        setpoint=Stamped(value=Valve.SWITCH_BRANCH, timestamp=_ZERO_TIME)
    ),
)


class ThrustersControl(Control):
    def __init__(
        self, parameters: ThrustersParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)

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
                    self._set_heat_dump_to_recovery,
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
                    self._set_heat_dump_to_cooling,
                    self._set_cooling_flow_setpoints,
                ],
            ),
            State(
                name="cooldown",
                on_enter=[
                    self._set_heat_dump_to_cooling,
                    self._set_cooldown_flow_setpoints,
                ],
            ),
        ]

        self._transitions = [
            {
                "trigger": "_check_overheat",
                "source": "recovery",
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
        self.thrusters_state_machine = Machine(
            model=self,
            states=self._states,
            transitions=self._transitions,
            initial="idle",
        )

        self._heat_dump_controller = Controller[Ratio, Celsius](
            _INITIAL_CONTROL_VALUES.thrusters_mix_exchanger.setpoint.value,
            parameters.cooling_temperature,
            parameters.heat_dump_tuning,
            self._time,
        )
        self._warmup_mix_controller = Controller[Ratio, Celsius](
            _INITIAL_CONTROL_VALUES.thrusters_mix_recovery.setpoint.value,
            parameters.warmup_temperature,
            parameters.warmup_mix_tuning,
            self._time,
        )
        self._pump_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.thrusters_pump_1.dutypoint.value,
            0,
            parameters.pump_tuning,
            self._time,
        )

        self._aft_recovery_temperature_controller = Controller[LMin, Celsius](
            parameters.thrusters_minimum_flow,
            parameters.recovery_temperature,
            parameters.aft_temperature_tuning,
            self._time,
            (
                parameters.thrusters_minimum_flow,
                parameters.thrusters_maximum_flow,
            ),
        )

        self._fwd_recovery_temperature_controller = Controller[LMin, Celsius](
            parameters.thrusters_minimum_flow,
            parameters.recovery_temperature,
            parameters.fwd_temperature_tuning,
            self._time,
            (
                parameters.thrusters_minimum_flow,
                parameters.thrusters_maximum_flow,
            ),
        )

        self._aft_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.thrusters_flowcontrol_aft.setpoint.value,
            0,
            parameters.aft_flow_balance_tuning,
            self._time,
        )

        self._fwd_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.thrusters_flowcontrol_fwd.setpoint.value,
            0,
            parameters.fwd_flow_balance_tuning,
            self._time,
        )

        self._most_recently_active_pump: None | Literal["pump1", "pump2"] = None
        self._active_pump: None | Pump = None

        self._flow_balance_controller = FlowBalanceController(
            [
                self._current_values.thrusters_flowcontrol_aft,
                self._current_values.thrusters_flowcontrol_fwd,
            ],
            [self._aft_flow_controller, self._fwd_flow_controller],
            self._active_pump,
            self._pump_controller,
            self._time,
        )

    @property
    def parameters(self) -> ThrustersParameters:
        return self._parameters

    @staticmethod
    def modes() -> list[str]:
        return ["idle", "cooling", "recovery", "cooldown"]

    @staticmethod
    def initial_mode() -> str:
        return "idle"

    @property
    def mode(self) -> Literal["idle", "cooling", "recovery", "cooldown"]:
        return self.state  # type: ignore

    def initial(self) -> ControlResult[ThrustersControlValues]:
        return ControlResult(self._time(), self._current_values)

    def control(
        self, sensor_values: ThrustersSensorValues
    ) -> ControlResult[ThrustersControlValues]:
        self._check_pcs_mode(sensor_values)  # type: ignore
        self._control_heat_dump(sensor_values)

        if self.mode == "recovery":
            self._set_recovery_flow_setpoints(sensor_values)
            self._control_warmup_mix(sensor_values)

        self._control_flow_balance(sensor_values)

        return ControlResult(self._time(), self._current_values)

    def _is_overheating(self, sensor_values: ThrustersSensorValues):
        return (
            sensor_values.thrusters_temperature_supply.temperature.value is not None
            and sensor_values.thrusters_temperature_supply.temperature.value > 90
        )

    def _cooled_down(self, sensor_values: ThrustersSensorValues):
        return (
            max(
                sensor_values.thrusters_temperature_fwd_return.temperature.value
                if sensor_values.thrusters_flow_fwd.flow.value > 1e-2
                else 0,
                sensor_values.thrusters_temperature_aft_return.temperature.value
                if sensor_values.thrusters_flow_aft.flow.value > 1e-2
                else 0,
            )
            < self._parameters.cooling_temperature
        )

    def _set_valves_to_cooling(self, sensor_values: ThrustersSensorValues):
        self._current_values.thrusters_switch_aft.setpoint = Stamped(
            value=Valve.SWITCH_STRAIGHT, timestamp=self._time()
        )
        self._current_values.thrusters_switch_fwd.setpoint = Stamped(
            value=Valve.SWITCH_STRAIGHT, timestamp=self._time()
        )
        self._current_values.thrusters_shutoff_recovery.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )

    def _set_valves_to_recovery(self, sensor_values: ThrustersSensorValues):
        self._current_values.thrusters_switch_aft.setpoint = Stamped(
            value=Valve.SWITCH_BRANCH, timestamp=self._time()
        )
        self._current_values.thrusters_switch_fwd.setpoint = Stamped(
            value=Valve.SWITCH_BRANCH, timestamp=self._time()
        )
        self._current_values.thrusters_shutoff_recovery.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )

    def _enable_flow_balancing(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.enable(
            [
                sensor_values.thrusters_aft.active.value,
                sensor_values.thrusters_fwd.active.value,
            ]
        )

    def _open_flowcontrol_valves(self, sensor_values: ThrustersSensorValues):
        self._current_values.thrusters_flowcontrol_aft.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )
        self._current_values.thrusters_flowcontrol_fwd.setpoint = Stamped(
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
        self._current_values.thrusters_mix_recovery.setpoint = Stamped(
            value=Valve.MIXING_B_TO_AB, timestamp=self._time()
        )

    def _set_recovery_temperature(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_setpoint(
            self._parameters.recovery_temperature
        )

    def _set_cooling_flow(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_setpoint(self._parameters.cooling_flow)

    def _set_heat_dump_to_recovery(self, sensor_values: ThrustersSensorValues):
        self._heat_dump_controller.setpoint = (
            self._parameters.maximum_supply_temperature
        )

    def _set_heat_dump_to_cooling(self, sensor_values: ThrustersSensorValues):
        self._heat_dump_controller.setpoint = self._parameters.cooling_temperature

    def _enable_heat_dump(self, sensor_values: ThrustersSensorValues):
        self._heat_dump_controller.enable()

    def _disable_heat_dump(self, sensor_values: ThrustersSensorValues):
        self._heat_dump_controller.disable()

    def _control_warmup_mix(self, sensor_values: ThrustersSensorValues):
        self._current_values.thrusters_mix_recovery.setpoint = Stamped(
            value=(
                self._warmup_mix_controller(
                    sensor_values.thrusters_temperature_recovery.temperature.value,
                )
            ),
            timestamp=self._time(),
        )

    def _control_heat_dump(self, sensor_values: ThrustersSensorValues):
        if self._heat_dump_controller.enabled():
            self._current_values.thrusters_mix_exchanger.setpoint = Stamped(
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
                sensor_values.thrusters_aft.active.value,
                sensor_values.thrusters_fwd.active.value,
            ]
        )

        flow_setpoints = [
            self._aft_recovery_temperature_controller(
                sensor_values.thrusters_temperature_aft_return.temperature.value,
            )
            if sensor_values.thrusters_aft.active.value
            else 0,
            self._fwd_recovery_temperature_controller(
                sensor_values.thrusters_temperature_fwd_return.temperature.value,
            )
            if sensor_values.thrusters_fwd.active.value
            else 0,
        ]

        self._flow_balance_controller.set_setpoints(flow_setpoints)

    def _set_cooling_flow_setpoints(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_active_valves(
            [
                sensor_values.thrusters_aft.active.value,
                sensor_values.thrusters_fwd.active.value,
            ]
        )
        self._flow_balance_controller.set_setpoint(25.0)

    def _set_cooldown_flow_setpoints(self, sensor_values: ThrustersSensorValues):
        # cool only the last used thrusters by not updating active valves
        self._flow_balance_controller.set_setpoint(25.0)

    def _control_flow_balance(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_pump(self._active_pump)
        self._flow_balance_controller(
            [
                sensor_values.thrusters_flow_aft.flow.value,
                sensor_values.thrusters_flow_fwd.flow.value,
            ]
        )

    def _pcs_off(self, sensor_values: ThrustersSensorValues):
        return sensor_values.thrusters_pcs.mode.value == PcsMode.OFF

    def _pcs_maneuvering(self, sensor_values: ThrustersSensorValues):
        return sensor_values.thrusters_pcs.mode.value == PcsMode.MANEUVERING

    def _pcs_propulsion_hydrogeneration(self, sensor_values: ThrustersSensorValues):
        return sensor_values.thrusters_pcs.mode.value in {
            PcsMode.PROPULSION,
            PcsMode.REGENERATION,
        }

    def _activate_pump(self, sensor_values: ThrustersSensorValues):
        if self._active_pump:
            raise Warning("A pump was already active upon selecting")
        else:
            if self._most_recently_active_pump == "pump1":
                self._most_recently_active_pump = "pump2"
                self._active_pump = self._current_values.thrusters_pump_2

            else:
                self._most_recently_active_pump = "pump1"
                self._active_pump = self._current_values.thrusters_pump_1

        self._active_pump.on = Stamped(value=True, timestamp=self._time())

    def _deactivate_pump(self, sensor_values: ThrustersSensorValues):
        if not self._active_pump:
            raise Warning("No pump active when deactivating")

        self._active_pump.on = Stamped(value=False, timestamp=self._time())
        self._active_pump.dutypoint = Stamped(value=0, timestamp=self._time())
        self._active_pump = None


class ThrustersAlarms(BaseAlarms):
    @alarm("A004", severity=Severity.ALARM)
    def check_overheating(
        self,
        sensor_values: ThrustersSensorValues,
        control_values: ThrustersControlValues,
    ) -> bool:
        return self.is_overheating(sensor_values)

    def is_overheating(self, sensor_values: ThrustersSensorValues) -> bool:
        return sensor_values.thrusters_temperature_supply.temperature.value > 95
