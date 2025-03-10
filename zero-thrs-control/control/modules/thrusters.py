from datetime import datetime

from input_output.base import Stamped
from input_output.control import Pump, Valve
from input_output.modules.thrusters import ThrustersControls


def simple_cooling(time) -> ThrustersControls:
    return ThrustersControls(
        thrusters_pump_1=Pump(
            dutypoint=Stamped(value=0.5, timestamp=time),
            on=Stamped(value=True, timestamp=time),
        ),
        thrusters_pump_2=Pump(
            dutypoint=Stamped(value=0.0, timestamp=time),
            on=Stamped(value=False, timestamp=time),
        ),
        thrusters_mix_aft=Valve(
            setpoint=Stamped(value=1, timestamp=time)
        ),  # irrelevant
        thrusters_mix_fwd=Valve(
            setpoint=Stamped(value=1, timestamp=time)
        ),  # irrelevant
        thrusters_mix_exchanger=Valve(setpoint=Stamped(value=0, timestamp=time)),
        thrusters_flowcontrol_aft=Valve(setpoint=Stamped(value=0, timestamp=time)),
        thrusters_flowcontrol_fwd=Valve(setpoint=Stamped(value=0, timestamp=time)),
        thrusters_shutoff_recovery=Valve(setpoint=Stamped(value=1, timestamp=time)),
        thrusters_switch_aft=Valve(setpoint=Stamped(value=0, timestamp=time)),
        thrusters_switch_fwd=Valve(setpoint=Stamped(value=0, timestamp=time)),
    )


def simple_recovery(time) -> ThrustersControls:
    return ThrustersControls(
        thrusters_pump_1=Pump(
            dutypoint=Stamped(value=0.5, timestamp=time),
            on=Stamped(value=True, timestamp=time),
        ),
        thrusters_pump_2=Pump(
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
