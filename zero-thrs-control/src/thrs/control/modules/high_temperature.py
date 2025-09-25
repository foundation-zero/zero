from datetime import datetime
from thrs.classes.control import Control, ControlResult
from thrs.control.modules.consumers import ConsumersControl, ConsumersParameters
from thrs.control.modules.pcm import PcmControl, PcmParameters
from thrs.control.modules.pvt import PvtControl, PvtParameters
from thrs.control.modules.thrusters import ThrustersControl, ThrustersParameters
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.modules.high_temperature import (
    HighTemperatureControlValues,
    HighTemperatureSensorValues,
)
from thrs.control.modules.thrusters import _INITIAL_CONTROL_VALUES as _THRUSTERS_INITIAL
from thrs.control.modules.pcm import _INITIAL_CONTROL_VALUES as _PCM_INITIAL
from thrs.control.modules.pvt import _INITIAL_CONTROL_VALUES as _PVT_INITIAL
from thrs.control.modules.consumers import _INITIAL_CONTROL_VALUES as _CONSUMERS_INITIAL

# TODO: don't import private variables


class HighTemperatureParameters(
    ThrustersParameters, PvtParameters, PcmParameters, ConsumersParameters
):
    pass


_INITIAL_CONTROL_VALUES = HighTemperatureControlValues(
    **{
        **_THRUSTERS_INITIAL.model_dump(),
        **_CONSUMERS_INITIAL.model_dump(),
        **_PCM_INITIAL.model_dump(),
        **_PVT_INITIAL.model_dump(),
    }
)


class HighTemperatureControl(
    Control[
        HighTemperatureSensorValues,
        HighTemperatureControlValues,
        HighTemperatureParameters,
    ]
):
    def __init__(self, parameters: HighTemperatureParameters, time: datetime) -> None:
        self._parameters = parameters
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)
        self._thrusters_control = ThrustersControl(parameters, time)
        self._pvt_control = PvtControl(parameters, time)
        self._pcm_control = PcmControl(parameters, time)
        self._consumers_control = ConsumersControl(parameters, time)

    def initial(self, time: datetime) -> ControlResult[HighTemperatureControlValues]:
        return ControlResult(time, self._current_values)

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
            HighTemperatureControlValues(
                **{
                    **self._thrusters_control._current_values.model_dump(),
                    **self._pvt_control._current_values.model_dump(),
                    **self._pcm_control._current_values.model_dump(),
                    **self._consumers_control._current_values.model_dump(),
                }
            ),
        )

    @property
    def mode(self) -> str | None:
        return None

    @property
    def modes(self) -> list[str]:
        return []

    @property
    def parameters(self) -> HighTemperatureParameters:
        return self._parameters


class HighTemperatureAlarms(BaseAlarms):
    pass
