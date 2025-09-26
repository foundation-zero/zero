from datetime import datetime
from thrs.classes.control import Control, ControlResult
from thrs.input_output.base import ThrsModel


class EmptyParameters(ThrsModel):
    pass


class ManualControl[SensorValues: ThrsModel, ControlValues: ThrsModel](
    Control[SensorValues, ControlValues, EmptyParameters]
):
    def __init__(self, control_values: ControlValues):
        self._control_values = control_values

    @property
    def parameters(self) -> EmptyParameters:
        return EmptyParameters()

    @property
    def modes(self) -> list[str]:
        return ["manual"]

    @property
    def mode(self) -> str:
        return "manual"

    def manual_controls(self, control_values: ControlValues):
        self._control_values = control_values

    def initial(self, time: datetime) -> ControlResult[ControlValues]:
        return ControlResult(time, self._control_values)

    def control(
        self, sensor_values: SensorValues, time: datetime
    ) -> ControlResult[ControlValues]:
        return ControlResult(time, self._control_values)
