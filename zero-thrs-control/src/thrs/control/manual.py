from datetime import datetime
from typing import Callable

from thrs.classes.control import Control, ControlResult
from thrs.input_output.base import ThrsValues


class EmptyParameters(ThrsValues):
    pass


class EmptyMode(ThrsValues):
    pass


class ManualControl[SensorValues: ThrsValues, ControlValues: ThrsValues](
    Control[SensorValues, ControlValues, EmptyParameters, EmptyMode]
):
    def __init__(
        self,
        control_values: ControlValues,
        time_fn: Callable[[], datetime],
        parameters: EmptyParameters = EmptyParameters(),
    ):
        self._control_values = control_values
        self._time_fn = time_fn

    @property
    def parameters(self) -> EmptyParameters:
        return EmptyParameters()

    @property
    def mode(self) -> EmptyMode:
        return EmptyMode()

    def manual_controls(self, control_values: ControlValues):
        self._control_values = control_values

    def initial(self) -> ControlResult[ControlValues]:
        return ControlResult(self._time_fn(), self._control_values)

    def control(self, sensor_values: SensorValues) -> ControlResult[ControlValues]:
        return ControlResult(self._time_fn(), self._control_values)

    def update_parameters(self, parameters: EmptyParameters):
        pass
