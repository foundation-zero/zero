from datetime import datetime
from classes.control import Control, ControlResult
from input_output.base import Stamped
from input_output.definitions.control import Pcm, Pump, Valve
from input_output.modules.pcm import PcmControlValues, PcmSensorValues

_ZERO_TIME = datetime.fromtimestamp(0)
_INITIAL_CONTROL_VALUES = PcmControlValues(
    pcm_pump=Pump(
        dutypoint=Stamped(value=0, timestamp=_ZERO_TIME),
        on=Stamped(value=False, timestamp=_ZERO_TIME),
    ),
    pcm_switch_charging_return=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pcm_flowcontrol_module_1=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pcm_flowcontrol_module_2=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pcm_flowcontrol_module_3=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pcm_flowcontrol_module_4=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pcm_switch_discharging=Valve(
        setpoint=Stamped(value=Valve.CLOSED, timestamp=_ZERO_TIME)
    ),
    pcm_switch_charging_supply=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pcm_switch_consumers=Valve(
        setpoint=Stamped(value=Valve.CLOSED, timestamp=_ZERO_TIME)
    ),
    pcm_module_1=Pcm(on=Stamped(value=False, timestamp=_ZERO_TIME)),
)


class PcmControl(Control[PcmSensorValues, PcmControlValues]):
    def __init__(self) -> None:
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)

    def initial(self, time: datetime) -> ControlResult[PcmControlValues]:
        return ControlResult(time, self._current_values)

    def control(self, sensor_values: PcmSensorValues, time: datetime) -> ControlResult:
        return ControlResult(time, self._current_values)
