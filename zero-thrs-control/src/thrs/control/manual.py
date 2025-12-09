from datetime import datetime
from typing import Callable
from thrs.classes.control import Control, ControlResult
from thrs.input_output.base import ThrsValues


class EmptyParameters(ThrsValues):
    pass


class ManualControl[SensorValues: ThrsValues, ControlValues: ThrsValues](
    Control[SensorValues, ControlValues, EmptyParameters]
):
    def __init__(self, control_values: ControlValues, time_fn: Callable[[], datetime]):
        self._control_values = control_values
        self._time_fn = time_fn

    @property
    def parameters(self) -> EmptyParameters:
        return EmptyParameters()

    @staticmethod
    def modes() -> list[str]:
        return ["manual"]

    @staticmethod
    def initial_mode() -> str:
        return "manual"

    @property
    def mode(self) -> str:
        return "manual"

    def manual_controls(self, control_values: ControlValues):
        self._control_values = control_values

    def initial(self) -> ControlResult[ControlValues]:
        return ControlResult(self._time_fn(), self._control_values)

    def control(self, sensor_values: SensorValues) -> ControlResult[ControlValues]:
        return ControlResult(self._time_fn(), self._control_values)

    def update_parameters(self, parameters: EmptyParameters):
        pass
