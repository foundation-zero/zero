from datetime import datetime
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from transitions import Machine, State

from control.controllers import (
    FlowBalanceController,
    HeatSupplyController,
    InvertedHeatDumpController,
    PumpFlowController,
)
from input_output.alarms import BaseAlarms, Severity, alarm
from input_output.base import ParameterMeta, Stamped
from input_output.definitions.control import Pump, Valve
from input_output.modules.thrusters import ThrustersControlValues, ThrustersSensorValues
from input_output.definitions.units import Celsius, LMin
from classes.control import Control, ControlResult


class ThrustersParameters(BaseModel):
    cooling_mix_setpoint: Annotated[Celsius, ParameterMeta("50-S016")] = 38
    recovery_thruster_flow: Annotated[
        LMin, Field(le=30), ParameterMeta("50-S003 and 50-S004")
    ] = 10  # TODO: add minimum from FDS
    cooling_thruster_flow: Annotated[
        LMin, Field(le=23.5), ParameterMeta("50-S014 and 50-S015")
    ] = 22  # TODO: add minimum from FDS
    max_inlet_temp: Celsius = 80  # TODO: add to FDS
    recovery_mix_setpoint: Annotated[Celsius, ParameterMeta("50-S007 and 50-S008")] = (
        60  # TODO: add minimum based on max inlet temperature of thrusters
    )


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
                    self._enable_recovery_mixes,
                    self._set_flow_balance_to_recovery,
                ],
                on_exit=self._disable_recovery_mixes,
            ),
            State(
                name="cooling",
                on_enter=[
                    self._set_valves_to_cooling,
                    self._enable_heat_dump_mix,
                    self._set_flow_balance_to_cooling,
                ],
                on_exit=self._disable_heat_dump_mix,
            ),
            State(
                name="safe",
                on_enter=[
                    self._set_valves_to_cooling,
                    self._enable_heat_dump_mix,
                    self._set_safe_pump_setpoint,
                    self._enable_thruster_flow_control,
                    self._set_flow_balance_to_cooling,
                ],
                on_exit=self._disable_heat_dump_mix,
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
                "source": "idle",
                "dest": "recovery",
                "conditions": self._pcs_propulsion_hydrogeneration,
            },
            {
                "trigger": "_check_pcs_mode",
                "source": ["idle", "recovery", "cooling"],
                "dest": "safe",
                "conditions": self._pcs_maneuvering,
            },
            {
                "trigger": "_check_pcs_mode",
                "source": ["recovery", "cooling", "safe"],
                "dest": "idle",
                "conditions": self._pcs_off,
            },
            # TODO: return from cooling to recovery
            # TODO: pressure loss
            # TODO: manual overrides
        ]
        self.thrusters_state_machine = Machine(
            model=self, states=self._states, transitions=self._transitions, initial="idle"
        )

        self._heat_dump_controller = InvertedHeatDumpController(
            _INITIAL_CONTROL_VALUES.thrusters_mix_exchanger.setpoint.value,
            parameters.cooling_mix_setpoint,
        )
        self._aft_heat_supply_controller = HeatSupplyController(
            _INITIAL_CONTROL_VALUES.thrusters_mix_aft.setpoint.value,
            parameters.recovery_mix_setpoint,
        )
        self._fwd_heat_supply_controller = HeatSupplyController(
            _INITIAL_CONTROL_VALUES.thrusters_mix_fwd.setpoint.value,
            parameters.recovery_mix_setpoint,
        )
        self._pump_flow_controller = PumpFlowController(
            _INITIAL_CONTROL_VALUES.thrusters_pump_1.dutypoint.value,
            0,
        )
        self._flow_balance_controller = FlowBalanceController([
            self._current_values.thrusters_flowcontrol_aft,
            self._current_values.thrusters_flowcontrol_fwd,
        ])
        self._most_recently_active_pump: None | Literal["pump1", "pump2"] = None
        self._active_pump: None | Pump = None

    @property
    def parameters(self) -> ThrustersParameters:
        return self._parameters

    @property
    def modes(self) -> list[str]:
        return list(self.thrusters_state_machine.states.keys())

    @property
    def mode(self) -> Literal["idle", "cooling", "recovery", "safe"]:
        return self.state  # type: ignore

    def initial(self, time: datetime) -> ControlResult[ThrustersControlValues]:
        return ControlResult(time, self._current_values)

    def control(
        self, sensor_values: ThrustersSensorValues, time: datetime
    ) -> ControlResult[ThrustersControlValues]:
        self._time = time

        self._check_pcs_mode(sensor_values)  # type: ignore

        self._control_recovery_mixes(sensor_values, time)
        self._control_heat_dump_mix(sensor_values, time)

        if self.mode == "cooling":
            self._cooling(sensor_values)
        elif self.mode == "recovery":
            self._recovery(sensor_values)
        elif self.mode == "safe":
            self._safe(sensor_values)

        self._control_flow_balance(sensor_values, time)

        return ControlResult(time, self._current_values)

    def _safe(self, sensor_values: ThrustersSensorValues):
        # In safe mode pump setpoints are set on mode transition
        self._control_pump(sensor_values)

    def _cooling(self, sensor_values: ThrustersSensorValues):
        self._pump_flow_controller.setpoint = (
            active_thrusters(sensor_values) * self._parameters.cooling_thruster_flow
        )
        self._flow_balance_controller.set_actives([
            sensor_values.thrusters_aft.active.value,
            sensor_values.thrusters_fwd.active.value,
        ])
        self._control_pump(sensor_values)

    def _recovery(self, sensor_values: ThrustersSensorValues):
        self._check_overheat(sensor_values)  # type: ignore

        self._pump_flow_controller.setpoint = (
            active_thrusters(sensor_values) * self._parameters.recovery_thruster_flow
        )
        self._flow_balance_controller.set_actives([
            sensor_values.thrusters_aft.active.value,
            sensor_values.thrusters_fwd.active.value,
        ])
        self._control_pump(sensor_values)

    def _is_overheating(self, sensor_values: ThrustersSensorValues):
        return (
            sensor_values.thrusters_temperature_supply.temperature.value
            > self._parameters.max_inlet_temp
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

    def _enable_recovery_mixes(self, sensor_values: ThrustersSensorValues):
        self._aft_heat_supply_controller.enable()
        self._fwd_heat_supply_controller.enable()

    def _disable_recovery_mixes(self, sensor_values: ThrustersSensorValues):
        self._aft_heat_supply_controller.disable()
        self._fwd_heat_supply_controller.disable()

    def _enable_thruster_flow_control(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_actives([True, True])

    def _disable_thruster_flow_control(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_actives([False, False])

    def _set_flow_balance_to_idle(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_setpoint(0)

    def _set_flow_balance_to_cooling(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_setpoint(
            self._parameters.cooling_thruster_flow
        )

    def _set_flow_balance_to_recovery(self, sensor_values: ThrustersSensorValues):
        self._flow_balance_controller.set_setpoint(
            self._parameters.recovery_thruster_flow
        )

    def _enable_heat_dump_mix(self, sensor_values: ThrustersSensorValues):
        self._heat_dump_controller.enable()

    def _disable_heat_dump_mix(self, sensor_values: ThrustersSensorValues):
        self._heat_dump_controller.disable()

    def _set_safe_pump_setpoint(self, sensor_values: ThrustersSensorValues):
        self._pump_flow_controller.setpoint = self._parameters.cooling_thruster_flow * 2

    def _control_recovery_mixes(
        self, sensor_values: ThrustersSensorValues, time: datetime
    ):
        self._current_values.thrusters_mix_aft.setpoint = Stamped(
            value=(
                self._aft_heat_supply_controller(
                    sensor_values.thrusters_temperature_aft_return.temperature.value,
                    self._time,
                )
            ),
            timestamp=time,
        )
        self._current_values.thrusters_mix_fwd.setpoint = Stamped(
            value=(
                self._fwd_heat_supply_controller(
                    sensor_values.thrusters_temperature_fwd_return.temperature.value,
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
        return sensor_values.thrusters_pcs.mode.value == "maneuvering"

    def _pcs_propulsion_hydrogeneration(self, sensor_values: ThrustersSensorValues):
        return sensor_values.thrusters_pcs.mode.value in {"propulsion", "regeneration"}

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
