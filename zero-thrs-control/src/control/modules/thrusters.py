from datetime import datetime
from typing import Literal
from pydantic import BaseModel
from transitions import Machine, State

from control.controllers import (
    HeatDumpController,
    HeatSupplyController,
    PumpFlowController,
)
from input_output.base import Stamped
from input_output.definitions.control import Pump, Valve
from input_output.modules.thrusters import ThrustersControlValues, ThrustersSensorValues
from input_output.definitions.units import Celsius, LMin
from classes.control import Control, ControlResult


class ThrustersParameters(BaseModel):
    cooling_mix_setpoint: Celsius
    recovery_thruster_flow: LMin
    cooling_thruster_flow: LMin
    max_temp: Celsius
    recovery_mix_setpoint: Celsius


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
        setpoint=Stamped(value=Valve.MIXING_A_TO_AB, timestamp=_ZERO_TIME)
    ),
    thrusters_mix_fwd=Valve(
        setpoint=Stamped(value=Valve.MIXING_A_TO_AB, timestamp=_ZERO_TIME)
    ),
    thrusters_mix_exchanger=Valve(
        setpoint=Stamped(
            value=Valve.MIXING_A_TO_AB,
            timestamp=_ZERO_TIME,
        )
    ),
    thrusters_flowcontrol_aft=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    thrusters_flowcontrol_fwd=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    thrusters_shutoff_recovery=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    thrusters_switch_aft=Valve(
        setpoint=Stamped(value=Valve.SWITCH_STRAIGHT, timestamp=_ZERO_TIME)
    ),
    thrusters_switch_fwd=Valve(
        setpoint=Stamped(value=Valve.SWITCH_STRAIGHT, timestamp=_ZERO_TIME)
    ),
)


states = [
    State(name="idle", on_exit="_activate_pump", on_enter="_deactivate_pump"),
    State(
        name="recovery",
        on_enter=[
            "_set_valves_to_recovery",
            "_enable_recovery_mixes",
        ],
        on_exit="_disable_recovery_mixes",
    ),
    State(
        name="cooling",
        on_enter=[
            "_set_valves_to_cooling",
            "_enable_heat_dump_mix",
        ],
        on_exit="_disable_heat_dump_mix",
    ),
    State(
        name="safe",
        on_enter=[
            "_set_valves_to_cooling",
            "_enable_heat_dump_mix",
            "_set_safe_pump_setpoint",
        ],
        on_exit="_disable_heat_dump_mix",
    ),
]


def active_thrusters(sensor_values: ThrustersSensorValues) -> int:
    return [
        sensor_values.thrusters_aft.active.value,
        sensor_values.thrusters_fwd.active.value,
    ].count(True)


class ThrustersControl(Control):
    def __init__(self, parameters: ThrustersParameters):
        self._parameters = parameters
        self._heat_dump_controller = HeatDumpController(
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
        self.machine = Machine(model=self, states=states, initial="idle")

        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)
        self._most_recently_active_pump: None | Literal["pump1", "pump2"] = None
        self._active_pump: None | Pump = None
        self._time = datetime.now()

    @property
    def mode(self) -> Literal["idle", "cooling", "recovery", "safe"]:
        return self.state  # type: ignore

    def initial(self, time: datetime) -> ControlResult[ThrustersControlValues]:
        return ControlResult(time, self._current_values)

    def _is_overheating(self, sensor_values: ThrustersSensorValues):
        return (
            sensor_values.thrusters_temperature_supply.temperature.value
            > self._parameters.max_temp
        )

    def _set_valves_to_cooling(self):
        self._current_values.thrusters_switch_aft.setpoint = Stamped(
            value=Valve.SWITCH_STRAIGHT, timestamp=self._time
        )
        self._current_values.thrusters_switch_fwd.setpoint = Stamped(
            value=Valve.SWITCH_STRAIGHT, timestamp=self._time
        )
        self._current_values.thrusters_shutoff_recovery.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time
        )

    def _set_valves_to_recovery(self):
        self._current_values.thrusters_switch_aft.setpoint = Stamped(
            value=Valve.SWITCH_BRANCH, timestamp=self._time
        )
        self._current_values.thrusters_switch_fwd.setpoint = Stamped(
            value=Valve.SWITCH_BRANCH, timestamp=self._time
        )
        self._current_values.thrusters_shutoff_recovery.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time
        )

    def _enable_recovery_mixes(self):
        self._aft_heat_supply_controller.enable()
        self._fwd_heat_supply_controller.enable()

    def _disable_recovery_mixes(self):
        self._aft_heat_supply_controller.disable()
        self._fwd_heat_supply_controller.disable()

    def _enable_heat_dump_mix(self):
        self._heat_dump_controller.enable()

    def _disable_heat_dump_mix(self):
        self._heat_dump_controller.disable()

    def _set_safe_pump_setpoint(self):
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

    def control(
        self, sensor_values: ThrustersSensorValues, time: datetime
    ) -> ControlResult[ThrustersControlValues]:
        self._time = time

        if self._is_overheating(sensor_values):
            self.to_cooling()  # type: ignore

        self._control_recovery_mixes(sensor_values, time)
        self._control_heat_dump_mix(sensor_values, time)

        if self.mode == "cooling":
            self._cooling(sensor_values)
        elif self.mode == "recovery":
            self._recovery(sensor_values)
        elif self.mode == "safe":
            self._safe(sensor_values)

        return ControlResult(time, self._current_values)

    def _safe(self, sensor_values: ThrustersSensorValues):
        if not self._active_pump:
            raise Warning("No pump active in safe mode")

        self._active_pump.dutypoint = Stamped(
            value=self._pump_flow_controller(
                sensor_values.thrusters_flow_aft.flow.value
                + sensor_values.thrusters_flow_fwd.flow.value,
                self._time,
            ),
            timestamp=self._time,
        )

    def _cooling(self, sensor_values: ThrustersSensorValues):
        self._pump_flow_controller.setpoint = (
            active_thrusters(sensor_values) * self._parameters.cooling_thruster_flow
        )
        self._safe(sensor_values)

    def _recovery(self, sensor_values: ThrustersSensorValues):
        if not self._active_pump:
            raise Warning("No pump active in recovery mode")

        self._pump_flow_controller.setpoint = (
            active_thrusters(sensor_values) * self._parameters.recovery_thruster_flow
        )
        self._active_pump.dutypoint = Stamped(
            value=self._pump_flow_controller(
                sensor_values.thrusters_flow_aft.flow.value
                + sensor_values.thrusters_flow_fwd.flow.value,
                self._time,
            ),
            timestamp=self._time,
        )

    def _activate_pump(self):
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

    def _deactivate_pump(self):
        if not self._active_pump:
            raise Warning("No pump active when deactivating")

        self._active_pump.on = Stamped(value=False, timestamp=self._time)
        self._active_pump = None
        self._pump_flow_controller.disable()
