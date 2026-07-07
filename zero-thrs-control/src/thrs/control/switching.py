from typing import Literal

from thrs.classes.control import Control
from thrs.control.manual import ManualControl
from thrs.input_output.base import ThrsValues


class SwitchingControlMode[M](ThrsValues):
    automatic_mode: M | None

    @property
    def automatic(self) -> bool:
        return self.automatic_mode is not None


class AutomationMode(ThrsValues):
    mode: Literal["manual", "automatic"]


class SwitchingControl[
    SensorValues: ThrsValues,
    ControlValues: ThrsValues,
    ControlParameters: ThrsValues,
    ControlMode,
    ControllerState: ThrsValues,
](
    Control[
        SensorValues,
        ControlValues,
        ControlParameters,
        ControlMode,
        ControllerState,
    ]
):
    def __init__(
        self,
        manual: ManualControl[SensorValues, ControlValues],
        automatic: Control[
            SensorValues,
            ControlValues,
            ControlParameters,
            ControlMode,
            ControllerState,
        ],
    ):
        self._manual_control = manual
        self._automatic_control = automatic
        self._mode: Literal["manual", "automatic"] = "manual"

    def initial(
        self,
    ) -> tuple[ControlValues, ControllerState]:
        return (
            self._manual_control.initial()[0],
            self._automatic_control.initial()[1],
        )

    def control(
        self, sensor_values: SensorValues
    ) -> tuple[ControlValues, ControllerState]:
        if self._mode == "manual":
            control_values, _ = self._manual_control.control(sensor_values)
            _, controller_state = self._automatic_control.initial()
            return control_values, controller_state
        else:
            return self._automatic_control.control(sensor_values)

    def switch_mode(self, mode: AutomationMode):
        self._mode = mode.mode

    @property
    def parameters(self) -> ControlParameters:
        return self._automatic_control.parameters

    def update_parameters(self, parameters: ControlParameters):
        self._automatic_control.update_parameters(parameters)

    @staticmethod
    def modes() -> list[AutomationMode]:
        return [AutomationMode(mode="manual"), AutomationMode(mode="automatic")]

    @staticmethod
    def initial_mode() -> AutomationMode:
        return AutomationMode(mode="manual")

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

    @property
    def manual_controls(self) -> ControlValues:
        return self._manual_control.controls

    def update_manual_controls(self, values: ControlValues):
        self._manual_control.update_controls(values)
