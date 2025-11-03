from datetime import datetime
from typing import Callable
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
    def __init__(
        self, parameters: HighTemperatureParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)
        self._thrusters_control = ThrustersControl(parameters, self._time)
        self._pvt_control = PvtControl(parameters, self._time)
        self._pcm_control = PcmControl(parameters, self._time)
        self._consumers_control = ConsumersControl(parameters, self._time)

    def initial(self) -> ControlResult[HighTemperatureControlValues]:
        return ControlResult(self._time(), self._current_values)

    def control(
        self, sensor_values: HighTemperatureSensorValues
    ) -> ControlResult[HighTemperatureControlValues]:
        self._thrusters_control.control(sensor_values)
        self._pvt_control.control(sensor_values)
        self._consumers_control.control(sensor_values)
        self._pcm_control.control(sensor_values)

        return ControlResult(
            self._time(),
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

    @staticmethod
    def modes() -> list[str]:
        return [""]

    @staticmethod
    def initial_mode() -> str:
        return ""

    @property
    def parameters(self) -> HighTemperatureParameters:
        return self._parameters

    def update_parameters(self, parameters: HighTemperatureParameters):
        pass


class HighTemperatureAlarms(BaseAlarms):
    pass
