from typing import Optional
from pydantic import BaseModel

from control.controllers import HeatDumpController
from input_output.base import Stamped
from input_output.definitions.control import Pump, Valve
from input_output.modules.thrusters import ThrustersControlValues, ThrustersSensorValues
from input_output.definitions.units import Celsius
from classes.control import Control


class ThrustersSetpoints(BaseModel):
    cooling_mix_setpoint: Celsius


class ThrustersControl(Control):
    def __init__(self, setpoints: ThrustersSetpoints):
        self._setpoints = setpoints
        self._heat_dump_controller = HeatDumpController(setpoints.cooling_mix_setpoint)

    def initial(self) -> ThrustersControlValues:
        return self.simple_cooling(None)

    def control(self, sensor_values) -> ThrustersControlValues:
        return self.simple_cooling(None)

    def simple_cooling(
        self, sensor_values: Optional[ThrustersSensorValues]
    ) -> ThrustersControlValues:
        return ThrustersControlValues(
            thrusters_pump1=Pump(
                dutypoint=Stamped.stamp(value=0.5),
                on=Stamped.stamp(value=True),
            ),
            thrusters_pump2=Pump(
                dutypoint=Stamped.stamp(value=0.0),
                on=Stamped.stamp(value=False),
            ),
            thrusters_mix_aft=Valve(setpoint=Stamped.stamp(value=1)),  # irrelevant
            thrusters_mix_fwd=Valve(setpoint=Stamped.stamp(value=1)),  # irrelevant
            thrusters_mix_exchanger=Valve(
                setpoint=Stamped.stamp(
                    value=self._heat_dump_controller(
                        sensor_values.thrusters_temperature_supply.temperature.value if sensor_values else 0
                    ),
                )
            ),
            thrusters_flowcontrol_aft=Valve(setpoint=Stamped.stamp(value=0)),
            thrusters_flowcontrol_fwd=Valve(setpoint=Stamped.stamp(value=0)),
            thrusters_shutoff_recovery=Valve(setpoint=Stamped.stamp(value=1)),
            thrusters_switch_aft=Valve(setpoint=Stamped.stamp(value=0)),
            thrusters_switch_fwd=Valve(setpoint=Stamped.stamp(value=0)),
        )

    def simple_recovery(self) -> ThrustersControlValues:
        # recovery without mixing
        return ThrustersControlValues(
            thrusters_pump1=Pump(
                dutypoint=Stamped.stamp(value=0.5),
                on=Stamped.stamp(value=True),
            ),
            thrusters_pump2=Pump(
                dutypoint=Stamped.stamp(value=0.0),
                on=Stamped.stamp(value=False),
            ),
            thrusters_mix_aft=Valve(setpoint=Stamped.stamp(value=0)),
            thrusters_mix_fwd=Valve(setpoint=Stamped.stamp(value=0)),
            thrusters_mix_exchanger=Valve(
                setpoint=Stamped.stamp(value=0)
            ),  # irrelevant
            thrusters_flowcontrol_aft=Valve(setpoint=Stamped.stamp(value=0)),
            thrusters_flowcontrol_fwd=Valve(setpoint=Stamped.stamp(value=0)),
            thrusters_shutoff_recovery=Valve(setpoint=Stamped.stamp(value=0)),
            thrusters_switch_aft=Valve(setpoint=Stamped.stamp(value=1)),
            thrusters_switch_fwd=Valve(setpoint=Stamped.stamp(value=1)),
        )
