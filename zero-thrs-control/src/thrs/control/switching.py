from typing import Literal, cast

from thrs.classes.control import Control
from thrs.classes.machine_state_logger import (
    MachineStateLoggingServiceNoop,
    StateLogger,
)
from thrs.control.manual import EmptyParameters, ManualControl
from thrs.input_output.base import ThrsValues
from thrs.input_output.sensor_values import AmcsModeSensorValues

type ControlModes = Literal["manual", "automatic"]


class SwitchingControlMode[Mode](ThrsValues):
    automatic_mode: Mode | None

    @property
    def automatic(self) -> bool:
        return self.automatic_mode is not None


class AutomationMode(ThrsValues):
    mode: ControlModes


class Switching[
    SensorValues: AmcsModeSensorValues,
    ControlValues: ThrsValues,
    ControlParameters: ThrsValues,
    ControlMode,
    ControllerState: ThrsValues,
]:
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
        self._mode: ControlModes = "manual"
        self._parameters = cast(ControlParameters, EmptyParameters())
        self.state_logger: StateLogger = MachineStateLoggingServiceNoop()

    @property
    def automatic_control(self):
        return self._automatic_control

    @property
    def manual_control(self):
        return self._manual_control

    def initial(
        self,
    ) -> tuple[ControlValues, ControllerState]:
        return (
            self._manual_control.initial()[0],
            self._automatic_control.initial()[1],
        )

    def control(
        self,
        sensor_values: SensorValues,
        actuated_control_values: ControlValues | None = None,
    ) -> tuple[ControlValues, ControllerState]:
        # When the AMCS is not in advisory mode it is in control itself: we keep the
        # manual controls tracking what it actually actuated and force manual mode, so
        # we cannot stay "automatic" while not the acting controller.
        if not sensor_values.mode.is_advisory:
            if actuated_control_values is not None:
                self._manual_control.update_controls(actuated_control_values)
            self._mode = "manual"

        if self.control_mode == "manual":
            control_values, _ = self._manual_control.control(sensor_values)
            _, controller_state = self._automatic_control.initial()
            return control_values, controller_state
        control_values, controller_state = self._automatic_control.control(
            sensor_values
        )

        # Keep the manual controls tracking the control output, so switching doesn't jump controls
        self._manual_control.update_controls(control_values)
        return control_values, controller_state

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
            if self.control_mode == "manual"
            else SwitchingControlMode(automatic_mode=self._automatic_control.mode)
        )

    @property
    def automatic(self) -> bool:
        return self.control_mode == "automatic"

    @property
    def manual(self) -> bool:
        return self.control_mode == "manual"

    @property
    def control_mode(self) -> ControlModes:
        return self._mode

    @property
    def manual_controls(self) -> ControlValues:
        return self._manual_control.controls

    def update_manual_controls(self, values: ControlValues):
        self._manual_control.update_controls(values)
