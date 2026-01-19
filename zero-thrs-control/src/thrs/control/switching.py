from typing import Literal
from thrs.classes.control import Control, ControlResult
from thrs.control.manual import ManualControl
from thrs.input_output.base import ThrsValues


class SwitchingControlMode[T](ThrsValues):
    automatic_mode: T | None

    @property
    def automatic(self) -> bool:
        return self.automatic_mode is not None


class SwitchingControl[
    SensorValues: ThrsValues,
    ControlValues: ThrsValues,
    P: ThrsValues,
    Mode,
](Control[SensorValues, ControlValues, P, Mode]):
    def __init__(
        self,
        manual: ManualControl[SensorValues, ControlValues],
        automatic: Control[SensorValues, ControlValues, P, Mode],
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
    def mode(self) -> SwitchingControlMode[Mode]:
        return (
            SwitchingControlMode(automatic_mode=None)
            if self._mode == "manual"
            else SwitchingControlMode(automatic_mode=self._automatic.mode)
        )

    @property
    def automatic(self) -> bool:
        return self._mode == "automatic"

    def manual_controls(self, values: ControlValues):
        self._manual.manual_controls(values)
