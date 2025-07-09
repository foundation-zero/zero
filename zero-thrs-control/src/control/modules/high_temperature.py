from datetime import datetime
from classes.control import Control, ControlResult
from control.modules.consumers import ConsumersControl, ConsumersParameters
from control.modules.pcm import PcmControl, PcmParameters
from control.modules.pvt import PvtControl, PvtParameters
from control.modules.thrusters import ThrustersControl, ThrustersParameters
from input_output.alarms import BaseAlarms
from input_output.modules.high_temperature import (
    HighTemperatureControlValues,
    HighTemperatureSensorValues,
)
from control.modules.thrusters import _INITIAL_CONTROL_VALUES as _THRUSTERS_INITIAL
from control.modules.pcm import _INITIAL_CONTROL_VALUES as _PCM_INITIAL
from control.modules.pvt import _INITIAL_CONTROL_VALUES as _PVT_INITIAL
from control.modules.consumers import _INITIAL_CONTROL_VALUES as _CONSUMERS_INITIAL
#TODO: don't import private variables

class HighTemperatureParameters(
    ThrustersParameters, PvtParameters, PcmParameters, ConsumersParameters
):
    pass


_INITIAL_CONTROL_VALUES = HighTemperatureControlValues(**{
    **_THRUSTERS_INITIAL.model_dump(),
    **_CONSUMERS_INITIAL.model_dump(),
    **_PCM_INITIAL.model_dump(),
    **_PVT_INITIAL.model_dump(),
})


class HighTemperatureControl(
    Control[HighTemperatureSensorValues, HighTemperatureControlValues]
):
    def __init__(self, parameters: HighTemperatureParameters) -> None:
        self._parameters = parameters
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)
        self._thrusters_control = ThrustersControl(parameters)
        self._pvt_control = PvtControl(parameters)
        self._pcm_control = PcmControl(parameters)
        self._consumers_control = ConsumersControl(parameters)

    def initial(self, time: datetime) -> ControlResult[HighTemperatureControlValues]:
        return ControlResult(
            time, self._current_values
        )

    def control(
        self, sensor_values: HighTemperatureSensorValues, time: datetime
    ) -> ControlResult[HighTemperatureControlValues]:
        self._time = time

        self._thrusters_control.control(sensor_values, time)
        self._pvt_control.control(sensor_values, time)
        self._consumers_control.control(sensor_values, time)
        self._pcm_control.control(sensor_values, time)

        return ControlResult(
            time,
            HighTemperatureControlValues(**{
                **self._thrusters_control._current_values.model_dump(),
                **self._pvt_control._current_values.model_dump(),
                **self._pcm_control._current_values.model_dump(),
                **self._consumers_control._current_values.model_dump(),
            }),
        )

    @property
    def mode(self) -> str | None:
        return None

class HighTemperatureAlarms(BaseAlarms):
    pass
