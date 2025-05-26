from datetime import datetime
from classes.control import Control, ControlResult
from input_output.base import Stamped
from input_output.definitions.control import Valve
from input_output.modules.consumers import ConsumersControlValues, ConsumersSensorValues

_ZERO_TIME = datetime.fromtimestamp(0)
_INITIAL_CONTROL_VALUES = ConsumersControlValues(
    consumers_switch_fahrenheit_direct_supply=Valve(
        setpoint=Stamped(value=Valve.SWITCH_STRAIGHT, timestamp=_ZERO_TIME)
    ),
    consumers_flowcontrol_bypass=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    consumers_flowcontrol_boosting=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    consumers_flowcontrol_fahrenheit=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    consumers_switch_fahrenheit_exchanger=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    consumers_switch_fahrenheit_direct_return=Valve(
        setpoint=Stamped(value=Valve.CLOSED, timestamp=_ZERO_TIME)
    ),
    consumers_switch_boosting=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
)


class ConsumersControl(Control[ConsumersSensorValues, ConsumersControlValues]):
    def __init__(self) -> None:
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)

    def initial(self, time: datetime) -> ControlResult[ConsumersControlValues]:
        return ControlResult(time, self._current_values)

    def control(
        self, sensor_values: ConsumersSensorValues, time: datetime
    ) -> ControlResult:
        return ControlResult(time, self._current_values)
