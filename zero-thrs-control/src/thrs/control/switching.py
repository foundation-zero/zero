from typing import Literal
from thrs.classes.control import Control, ControlResult
from thrs.control.manual import ManualControl
from thrs.input_output.base import ThrsValues


class SwitchingControlMode[M](ThrsValues):
    automatic_mode: M | None

    @property
    def automatic(self) -> bool:
        return self.automatic_mode is not None


class SwitchingControl[
    SensorValues: ThrsValues,
    ControlValues: ThrsValues,
    ControlParameters: ThrsValues,
    ControlMode,
](Control[SensorValues, ControlValues, ControlParameters, ControlMode]):
    def __init__(
        self,
        manual: ManualControl[SensorValues, ControlValues],
        automatic: Control[SensorValues, ControlValues, ControlParameters, ControlMode],
    ):
        self._manual_control = manual
        self._automatic_control = automatic
        self._mode: Literal["manual", "automatic"] = "manual"

    def initial(self) -> ControlResult[ControlValues]:
        return self._manual_control.initial()

    def control(self, sensor_values: SensorValues):
        if self._mode == "manual":
            return self._manual_control.control(sensor_values)
        else:
            return self._automatic_control.control(sensor_values)

    def switch_mode(self, mode: Literal["manual", "automatic"]):
        self._mode = mode

    @property
    def parameters(self) -> ControlParameters:
        return self._automatic_control.parameters

    def update_parameters(self, parameters: ControlParameters):
        self._automatic_control.update_parameters(parameters)

    @staticmethod
    def modes() -> list[str]:
        return ["manual", "automatic"]

    @staticmethod
    def initial_mode() -> str:
        return "manual"

    @property
    def mode(self) -> SwitchingControlMode[ControlMode]:
        return (
            SwitchingControlMode(automatic_mode=None)
            if self._mode == "manual"
            else SwitchingControlMode(automatic_mode=self._automatic_control.mode)
        )

    @property
    def automatic(self) -> bool:
        return self._mode == "automatic"

    def manual_controls(self, values: ControlValues):
        self._manual_control.manual_controls(values)
