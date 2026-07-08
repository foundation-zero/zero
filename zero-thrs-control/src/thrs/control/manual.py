from datetime import datetime
from typing import Callable

from thrs.classes.control import Control
from thrs.input_output.base import ThrsValues


class EmptyParameters(ThrsValues):
    pass


class EmptyMode(ThrsValues):
    pass


class EmptyControllerState(ThrsValues):
    pass


class ManualControl[SensorValues: ThrsValues, ControlValues: ThrsValues](
    Control[
        SensorValues, ControlValues, EmptyParameters, EmptyMode, EmptyControllerState
    ]
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

    @property
    def controls(self) -> ControlValues:
        return self._control_values

    def update_controls(self, control_values: ControlValues):
        self._control_values = control_values

    def initial(self) -> tuple[ControlValues, EmptyControllerState]:
        return (self._control_values, EmptyControllerState())

    def control(
        self, sensor_values: SensorValues
    ) -> tuple[ControlValues, EmptyControllerState]:
        return (self._control_values, EmptyControllerState())

    def update_parameters(self, parameters: EmptyParameters):
        pass
