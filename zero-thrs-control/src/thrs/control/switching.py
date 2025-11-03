from typing import Literal
from thrs.classes.control import Control, ControlResult
from thrs.control.manual import ManualControl
from thrs.input_output.base import ThrsModel


class SwitchingControl[SensorValues: ThrsModel, ControlValues: ThrsModel, P: ThrsModel](
    Control[SensorValues, ControlValues, P]
):
    def __init__(
        self,
        manual: ManualControl[SensorValues, ControlValues],
        automatic: Control[SensorValues, ControlValues, P],
    ):
        self._manual = manual
        self._automatic = automatic
        self._mode: Literal["manual", "automatic"] = "manual"

    def initial(self) -> ControlResult[ControlValues]:
        return self._manual.initial()

    def control(self, sensor_values: SensorValues):
        if self._mode == "manual":
            return self._manual.control(sensor_values)
        else:
            return self._automatic.control(sensor_values)

    def switch_mode(self, mode: Literal["manual", "automatic"]):
        self._mode = mode

    @property
    def parameters(self) -> P:
        return self._automatic.parameters

    def update_parameters(self, parameters: P):
        self._automatic.update_parameters(parameters)

    @staticmethod
    def modes() -> list[str]:
        return ["manual", "automatic"]

    @staticmethod
    def initial_mode() -> str:
        return "manual"

    @property
    def mode(self) -> str | None:
        return self._mode

    @property
    def automatic(self) -> bool:
        return self._mode == "automatic"
