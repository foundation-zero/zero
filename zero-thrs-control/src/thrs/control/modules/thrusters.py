from datetime import datetime
from typing import Literal
from pydantic import BaseModel, model_validator

from transitions import Machine, State

from thrs.control.controllers import Controller, FlowBalanceController
from thrs.input_output.alarms import BaseAlarms, Severity, alarm
from thrs.input_output.base import ParameterMeta, Stamped
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
)
from thrs.input_output.definitions.units import Celsius, LMin, PcsMode, Ratio, Tuning
from thrs.classes.control import Control, ControlResult


class ThrustersParameters(BaseModel):
    maximum_recovery_temperature: Celsius = 70  # TODO: use field or model validator to set dependencies between parameters
    cooling_temperature: Celsius = 38
    recovery_temperature: Celsius = 63
    warmup_temperature: Celsius = 60
    pump_tuning: Tuning = (0.01, 0.001, 0)
    warmup_mix_tuning: Tuning = (-0.05, -0.001, 0)
    heat_dump_tuning: Tuning = (0.05, 0.01, 0)
    flow_balance_tuning: Tuning = (0.01, 0.001, 0)

    @model_validator(mode="after")
    def check_temperature_setpoints(self):
        if self.maximum_recovery_temperature < self.recovery_temperature:
            raise ValueError("Maximum recovery temperature must be greater than recovery temperature")
        if self.recovery_temperature < self.warmup_temperature:
            raise ValueError("Recovery temperature must be greater than warmup temperature")
        if self.warmup_temperature < self.cooling_temperature:
            raise ValueError("Warmup temperature must be greater than cooling temperature")
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
    thrusters_mix_aft=Valve(
        setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=_ZERO_TIME)
    ),
    thrusters_mix_fwd=Valve(
        setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=_ZERO_TIME)
    ),
    thrusters_mix_exchanger=Valve(
        setpoint=Stamped(
            value=Valve.MIXING_B_TO_AB,
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


def active_thrusters(sensor_values: ThrustersSensorValues) -> int:
    return [
        sensor_values.thrusters_aft.active.value,
        sensor_values.thrusters_fwd.active.value,
    ].count(True)


class ThrustersControl(Control):
    def __init__(self, parameters: ThrustersParameters):
        self._parameters = parameters
        self._time = datetime.now()
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)

        self._states = [
            State(
                name="idle",
                on_enter=[
                    self._deactivate_pump,
                    self._disable_thruster_flow_control,
                    self._set_flow_balance_to_idle,
                    self._set_valves_to_recovery,
                ],
                on_exit=self._activate_pump,
            ),
            State(
                name="recovery",
                on_enter=[
                    self._set_valves_to_recovery,
                    self._enable_warmup_mix,
                    self._set_heat_dump_to_recovery,
                    self._set_flow_balance_to_recovery,
                ],
                on_exit=self._disable_warmup_mix,
            ),
            State(
                name="cooling",
                on_enter=[
                    self._set_valves_to_cooling,
                    self._set_heat_dump_to_cooling,
                    self._set_flow_balance_to_cooling,
                ],
                on_exit=self._disable_heat_dump_mix,
            ),
            State(
                name="cooldown",
                on_enter=[self._set_heat_dump_to_cooling],
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
                "source": ["cooldown"],
                "dest": "idle",
                "conditions": self._pcs_off,
            },
            # TODO: alarms
            # TODO: manual
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
        )
        self._warmup_mix_controller = Controller[Ratio, Celsius](
            _INITIAL_CONTROL_VALUES.thrusters_warmup_mix.setpoint.value,
            parameters.warmup_temperature,
            parameters.warmup_mix_tuning,
        )
        self._pump_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.thrusters_pump_1.dutypoint.value,
            0,
            parameters.pump_tuning,
        )
        self._flow_balance_controller = FlowBalanceController(
            [
                self._current_values.thrusters_flowcontrol_aft,
                self._current_values.thrusters_flowcontrol_fwd,
            ],
            parameters.flow_balance_tuning,
        )
        self._most_recently_active_pump: None | Literal["pump1", "pump2"] = None
        self._active_pump: None | Pump = None

    @property
    def parameters(self) -> ThrustersParameters:
        return self._parameters

    @property
    def modes(self) -> list[str]:
        return list(self.thrusters_state_machine.states.keys())

    @property
    def mode(self) -> Literal["idle", "cooling", "recovery", "cooldown"]:
        return self.state  # type: ignore

    def initial(self, time: datetime) -> ControlResult[ThrustersControlValues]:
        return ControlResult(time, self._current_values)

    def control(
        self, sensor_values: ThrustersSensorValues, time: datetime
    ) -> ControlResult[ThrustersControlValues]:
        self._time = time

        self._check_pcs_mode(sensor_values)  # type: ignore

        self._control_warmup_mix(sensor_values, time)
        self._control_heat_dump_mix(sensor_values, time)

        if self.mode == "cooling":
            self._cooling(sensor_values)
        elif self.mode == "recovery":
            self._recovery(sensor_values)

        self._control_flow_balance(sensor_values, time)

        return ControlResult(time, self._current_values)

    def _cooling(self, sensor_values: ThrustersSensorValues):
        self._pump_flow_controller.setpoint = (
            active_thrusters(sensor_values) * self._parameters.cooling_thruster_flow
        )
        self._flow_balance_controller.set_actives(
            [
                sensor_values.thrusters_aft.active.value,
                sensor_values.thrusters_fwd.active.value,
            ]
        )
        self._control_pump(sensor_values)

    def _recovery(self, sensor_values: ThrustersSensorValues):
        self._check_overheat(sensor_values)  # type: ignore

        self._pump_flow_controller.setpoint = (
            active_thrusters(sensor_values) * self._parameters.recovery_thruster_flow
        )
        self._flow_balance_controller.set_actives(
            [
                sensor_values.thrusters_aft.active.value,
                sensor_values.thrusters_fwd.active.value,
            ]
        )
        self._control_pump(sensor_values)

    def _is_overheating(self, sensor_values: ThrustersSensorValues):
        return (
            sensor_values.thrusters_temperature_supply.temperature.value
            > 90  # TODO: hardcoded?
        )

    def _set_valves_to_cooling(self, sensor_values: ThrustersSensorValues):
        self._current_values.thrusters_switch_aft.setpoint = Stamped(
            value=Valve.SWITCH_STRAIGHT, timestamp=self._time
        )
        self._current_values.thrusters_switch_fwd.setpoint = Stamped(
            value=Valve.SWITCH_STRAIGHT, timestamp=self._time
        )
        self._current_values.thrusters_shutoff_recovery.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time
        )

    def _set_valves_to_recovery(self, sensor_values: ThrustersSensorValues):
        self._current_values.thrusters_switch_aft.setpoint = Stamped(
            value=Valve.SWITCH_BRANCH, timestamp=self._time
        )
        self._current_values.thrusters_switch_fwd.setpoint = Stamped(
            value=Valve.SWITCH_BRANCH, timestamp=self._time
        )
        self._current_values.thrusters_shutoff_recovery.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time
        )

    def _enable_warmup_mix(self, sensor_values: ThrustersSensorValues):
        self._warmup_mix_controller.enable()

    def _disable_warmup_mix(self, sensor_values: ThrustersSensorValues):
        self._warmup_mix_controller.disable()

    # TODO:check
    def _enable_thruster_flow_control(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_actives([True, True])

    # TODO:check
    def _disable_thruster_flow_control(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_actives([False, False])

    # TODO: rename to .enable just as pid controllers?
    def _set_flow_balance_to_idle(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_setpoint(0)

    def _set_flow_balance_to_cooling(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_setpoint(self._parameters.cooling_temperature)

    def _set_flow_balance_to_recovery(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_setpoint(
            self._parameters.recovery_temperature
        )

    def _set_heat_dump_to_recovery(self, sensor_values: ThrustersSensorValues):
        self._heat_dump_controller.setpoint = self._parameters.recovery_temperature

    def _set_heat_dump_to_cooling(self, sensor_values: ThrustersSensorValues):
        self._heat_dump_controller.setpoint = self._parameters.cooling_temperature

    def _enable_heat_dump_mix(self, sensor_values: ThrustersSensorValues):
        self._heat_dump_controller.enable()

    def _disable_heat_dump_mix(self, sensor_values: ThrustersSensorValues):
        self._heat_dump_controller.disable()

    def _control_warmup_mix(self, sensor_values: ThrustersSensorValues, time: datetime):
        self._current_values.thrusters_warmup_mix.setpoint = Stamped(
            value=(
                self._warmup_mix_controller(
                    min(
                        sensor_values.thrusters_temperature_aft_return.temperature.value,
                        sensor_values.thrusters_temperature_fwd_return.temperature.value,
                    ),
                    self._time,
                )
            ),
            timestamp=time,
        )

    def _control_heat_dump_mix(
        self, sensor_values: ThrustersSensorValues, time: datetime
    ):
        self._current_values.thrusters_mix_exchanger.setpoint = Stamped(
            value=(
                self._heat_dump_controller(
                    sensor_values.thrusters_temperature_supply.temperature.value,
                    self._time,
                )
            ),
            timestamp=time,
        )

    def _control_flow_balance(
        self, sensor_values: ThrustersSensorValues, time: datetime
    ):
        self._flow_balance_controller(
            [
                sensor_values.thrusters_flow_aft.flow.value,
                sensor_values.thrusters_flow_fwd.flow.value,
            ],
            time,
        )

    def _control_pump(self, sensor_values: ThrustersSensorValues):
        if not self._active_pump:
            raise Warning("No pump active in recovery mode")

        self._active_pump.dutypoint = Stamped(
            value=self._pump_flow_controller(
                sensor_values.thrusters_flow_aft.flow.value
                + sensor_values.thrusters_flow_fwd.flow.value,
                self._time,
            ),
            timestamp=self._time,
        )

    def _pcs_off(self, sensor_values: ThrustersSensorValues):
        return sensor_values.thrusters_pcs.mode.value == "off"

    def _pcs_maneuvering(self, sensor_values: ThrustersSensorValues):
        return sensor_values.thrusters_pcs.mode.value == PcsMode.MANEUVRING

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

        self._active_pump.on = Stamped(value=True, timestamp=self._time)
        self._pump_flow_controller.enable()

    def _deactivate_pump(self, sensor_values: ThrustersSensorValues):
        if not self._active_pump:
            raise Warning("No pump active when deactivating")

        self._active_pump.on = Stamped(value=False, timestamp=self._time)
        self._active_pump = None
        self._pump_flow_controller.disable()


class ThrustersAlarms(BaseAlarms):
    @alarm("A004", severity=Severity.ALARM)
    def check_overheating(
        self,
        sensor_values: ThrustersSensorValues,
        control_values: ThrustersControlValues,
        control: ThrustersControl,
    ) -> bool:
        return control._is_overheating(sensor_values)
