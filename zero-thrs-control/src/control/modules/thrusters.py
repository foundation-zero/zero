from datetime import datetime
from typing import Literal
from pydantic import BaseModel

from control.controllers import HeatDumpController
from input_output.base import Stamped
from input_output.definitions.control import Pump, Valve
from input_output.modules.thrusters import ThrustersControlValues, ThrustersSensorValues
from input_output.definitions.units import Celsius
from classes.control import Control, ControlResult


class ThrustersSetpoints(BaseModel):
    cooling_mix_setpoint: Celsius


_ZERO_TIME = datetime.fromtimestamp(0)
_INITIAL_CONTROL_VALUES = ThrustersControlValues(
    thrusters_pump1=Pump(
        dutypoint=Stamped(value=0.0, timestamp=_ZERO_TIME),
        on=Stamped(value=False, timestamp=_ZERO_TIME),
    ),
    thrusters_pump2=Pump(
        dutypoint=Stamped(value=0.0, timestamp=_ZERO_TIME),
        on=Stamped(value=False, timestamp=_ZERO_TIME),
    ),
    thrusters_mix_aft=Valve(
        setpoint=Stamped(value=1.0, timestamp=_ZERO_TIME)
    ),  # irrelevant
    thrusters_mix_fwd=Valve(
        setpoint=Stamped(value=1.0, timestamp=_ZERO_TIME)
    ),  # irrelevant
    thrusters_mix_exchanger=Valve(
        setpoint=Stamped(
            value=1.0,
            timestamp=_ZERO_TIME,
        )
    ),
    thrusters_flowcontrol_aft=Valve(setpoint=Stamped(value=1.0, timestamp=_ZERO_TIME)),
    thrusters_flowcontrol_fwd=Valve(setpoint=Stamped(value=1.0, timestamp=_ZERO_TIME)),
    thrusters_shutoff_recovery=Valve(setpoint=Stamped(value=1.0, timestamp=_ZERO_TIME)),
    thrusters_switch_aft=Valve(setpoint=Stamped(value=1.0, timestamp=_ZERO_TIME)),
    thrusters_switch_fwd=Valve(setpoint=Stamped(value=1.0, timestamp=_ZERO_TIME)),
)


class ThrustersControl(Control):
    def __init__(self, setpoints: ThrustersSetpoints):
        self._setpoints = setpoints
        self._heat_dump_controller = HeatDumpController(setpoints.cooling_mix_setpoint)
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)
        self._most_recently_used_pump: None | Literal["pump1", "pump2"] = None

    def initial(self, time: datetime) -> ControlResult[ThrustersControlValues]:
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)
        return ControlResult(time, self._current_values)

    def control(
        self, sensor_values: ThrustersSensorValues, time: datetime
    ) -> ControlResult[ThrustersControlValues]:
        return ControlResult(time, self.simple_cooling(sensor_values, time))

    def simple_cooling(
        self, sensor_values: ThrustersSensorValues | None, time: datetime
    ) -> ThrustersControlValues:
        pump = self.select_pump()
        pump.on = Stamped(value=True, timestamp=time)
        pump.dutypoint = Stamped(value=0.5, timestamp=time)
        self._current_values.thrusters_mix_exchanger.setpoint = Stamped(
            value=(
                self._heat_dump_controller(
                    sensor_values.thrusters_temperature_supply.temperature.value
                )
                if sensor_values
                else 1.0
            ),
            timestamp=time,
        )
        self.select_mode("cooling", time)
        return self._current_values

    def simple_recovery(self, time: datetime) -> ThrustersControlValues:
        # recovery without mixing
        pump = self.select_pump()
        pump.on = Stamped(value=True, timestamp=time)
        pump.dutypoint = Stamped(value=0.5, timestamp=time)
        self._current_values.thrusters_mix_exchanger.setpoint = Stamped(
            value=1.0,
            timestamp=time,
        )
        self.select_mode("recovery", time)
        return self._current_values

    def select_mode(self, mode: Literal["cooling", "recovery"], time: datetime):
        switch_valve_position = Valve.SWITCH_STRAIGHT if mode == "cooling" else 0.0
        self._current_values.thrusters_switch_aft.setpoint = Stamped(
            value=switch_valve_position, timestamp=time
        )
        self._current_values.thrusters_switch_fwd.setpoint = Stamped(
            value=switch_valve_position, timestamp=time
        )

    def select_pump(self) -> Pump:
        active_pump = next(
            (
                pump
                for pump in [
                    self._current_values.thrusters_pump1,
                    self._current_values.thrusters_pump2,
                ]
                if pump.on.value
            ),
            None,
        )
        if active_pump:
            return active_pump
        else:
            if self._most_recently_used_pump == "pump1":
                self._most_recently_used_pump = "pump2"
                return self._current_values.thrusters_pump2
            else:
                self._most_recently_used_pump = "pump1"
                return self._current_values.thrusters_pump1
