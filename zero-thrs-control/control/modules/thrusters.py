from pydantic import BaseModel

from control.controllers import HeatDumpController
from input_output.base import Stamped
from input_output.definitions.control import Pump, Valve
from input_output.modules.thrusters import ThrustersControlValues, ThrustersSensorValues
from input_output.definitions.units import Celsius


class ThrustersSetpoints(BaseModel):
    cooling_mix_setpoint: Celsius


class ThrustersControl:
    def __init__(self, setpoints: ThrustersSetpoints):
        self._setpoints = setpoints
        self._heat_dump_controller = HeatDumpController(setpoints.cooling_mix_setpoint)

    def simple_cooling(
        self, sensor_values: ThrustersSensorValues, time
    ) -> ThrustersControlValues:
        return ThrustersControlValues(
            thrusters_pump1=Pump(
                dutypoint=Stamped(value=0.5, timestamp=time),
                on=Stamped(value=True, timestamp=time),
            ),
            thrusters_pump2=Pump(
                dutypoint=Stamped(value=0.0, timestamp=time),
                on=Stamped(value=False, timestamp=time),
            ),
            thrusters_mix_aft=Valve(
                setpoint=Stamped(value=1, timestamp=time)
            ),  # irrelevant
            thrusters_mix_fwd=Valve(
                setpoint=Stamped(value=1, timestamp=time)
            ),  # irrelevant
            thrusters_mix_exchanger=Valve(
                setpoint=Stamped(
                    value=self._heat_dump_controller(
                        sensor_values.thrusters_temperature_supply.temperature.value
                    ),
                    timestamp=time,
                )
            ),
            thrusters_flowcontrol_aft=Valve(setpoint=Stamped(value=0, timestamp=time)),
            thrusters_flowcontrol_fwd=Valve(setpoint=Stamped(value=0, timestamp=time)),
            thrusters_shutoff_recovery=Valve(setpoint=Stamped(value=1, timestamp=time)),
            thrusters_switch_aft=Valve(setpoint=Stamped(value=0, timestamp=time)),
            thrusters_switch_fwd=Valve(setpoint=Stamped(value=0, timestamp=time)),
        )

    def simple_recovery(self, time) -> ThrustersControlValues:
        # recovery without mixing
        return ThrustersControlValues(
            thrusters_pump1=Pump(
                dutypoint=Stamped(value=0.5, timestamp=time),
                on=Stamped(value=True, timestamp=time),
            ),
            thrusters_pump2=Pump(
                dutypoint=Stamped(value=0.0, timestamp=time),
                on=Stamped(value=False, timestamp=time),
            ),
            thrusters_mix_aft=Valve(setpoint=Stamped(value=0, timestamp=time)),
            thrusters_mix_fwd=Valve(setpoint=Stamped(value=0, timestamp=time)),
            thrusters_mix_exchanger=Valve(
                setpoint=Stamped(value=0, timestamp=time)
            ),  # irrelevant
            thrusters_flowcontrol_aft=Valve(setpoint=Stamped(value=0, timestamp=time)),
            thrusters_flowcontrol_fwd=Valve(setpoint=Stamped(value=0, timestamp=time)),
            thrusters_shutoff_recovery=Valve(setpoint=Stamped(value=0, timestamp=time)),
            thrusters_switch_aft=Valve(setpoint=Stamped(value=1, timestamp=time)),
            thrusters_switch_fwd=Valve(setpoint=Stamped(value=1, timestamp=time)),
        )
