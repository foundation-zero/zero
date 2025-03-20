from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from control.controllers import HeatDumpController
from input_output.base import Stamped
from input_output.definitions.control import Pump, Valve
from input_output.modules.thrusters import ThrustersControlValues, ThrustersSensorValues
from input_output.definitions.units import Celsius
from classes.control import Control, ControlResult


class ThrustersSetpoints(BaseModel):
    cooling_mix_setpoint: Celsius


class ThrustersControl(Control):
    def __init__(self, setpoints: ThrustersSetpoints):
        self._setpoints = setpoints
        self._heat_dump_controller = HeatDumpController(setpoints.cooling_mix_setpoint)

    def initial(self, time: datetime) -> ControlResult[ThrustersControlValues]:
        return ControlResult(time, self.simple_cooling(None, time))

    def control(self, sensor_values: ThrustersSensorValues, time: datetime) -> ControlResult[ThrustersControlValues]:
        return ControlResult(time, self.simple_cooling(None, time))

    def simple_cooling(
        self, sensor_values: Optional[ThrustersSensorValues], time: datetime
    ) -> ThrustersControlValues:
        return ThrustersControlValues(
            thrusters_pump1=Pump(
                dutypoint=Stamped(value=0.5, timestamp=time),
                on=Stamped(value=True, timestamp=time),
            ),
            thrusters_pump2=Pump(
                dutypoint=Stamped(value=0.0, timestamp = time),
                on=Stamped(value=False, timestamp = time),
            ),
            thrusters_mix_aft=Valve(setpoint=Stamped(value=1, timestamp = time)),  # irrelevant
            thrusters_mix_fwd=Valve(setpoint=Stamped(value=1, timestamp = time)),  # irrelevant
            thrusters_mix_exchanger=Valve(
                setpoint=Stamped(
                    value=self._heat_dump_controller(
                        sensor_values.thrusters_temperature_supply.temperature.value
                        if sensor_values
                        else 1
                    ),
                    timestamp = time
                )
            ),
            thrusters_flowcontrol_aft=Valve(setpoint=Stamped(value=1, timestamp = time)),
            thrusters_flowcontrol_fwd=Valve(setpoint=Stamped(value=1, timestamp = time)),
            thrusters_shutoff_recovery=Valve(setpoint=Stamped(value=0, timestamp = time)),
            thrusters_switch_aft=Valve(setpoint=Stamped(value=1, timestamp = time)),
            thrusters_switch_fwd=Valve(setpoint=Stamped(value=1, timestamp = time)),
        )

    def simple_recovery(self, time: datetime) -> ThrustersControlValues:
        # recovery without mixing
        return ThrustersControlValues(
            thrusters_pump1=Pump(
                dutypoint=Stamped(value=0.5, timestamp=time),
                on=Stamped(value=True, timestamp=time),
            ),
            thrusters_pump2=Pump(
                dutypoint=Stamped(value=0.0, timestamp = time),
                on=Stamped(value=False, timestamp = time),
            ),
            thrusters_mix_aft=Valve(setpoint=Stamped(value=1, timestamp = time)),
            thrusters_mix_fwd=Valve(setpoint=Stamped(value=1, timestamp = time)),
            thrusters_mix_exchanger=Valve(
                setpoint=Stamped(value=1, timestamp = time)
            ),  # irrelevant
            thrusters_flowcontrol_aft=Valve(setpoint=Stamped(value=1, timestamp = time)),
            thrusters_flowcontrol_fwd=Valve(setpoint=Stamped(value=1, timestamp = time)),
            thrusters_shutoff_recovery=Valve(setpoint=Stamped(value=1, timestamp = time)),
            thrusters_switch_aft=Valve(setpoint=Stamped(value=0, timestamp = time)),
            thrusters_switch_fwd=Valve(setpoint=Stamped(value=0, timestamp = time)),
        )
