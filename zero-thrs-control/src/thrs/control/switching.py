import logging

from thrs.classes.control import Control
from thrs.control.manual import ManualControl
from thrs.control.state import AutomationMode, ControlModes, ControlState
from thrs.input_output.base import ThrsValues
from thrs.input_output.root_types import AmcsModeSensorValues

logger = logging.getLogger(__name__)


class Switching[
    SensorValues: AmcsModeSensorValues,
    ControlValues: ThrsValues,
    ControlParameters: ThrsValues,
    ControlMode: ThrsValues,
    ControllerState: ControlState,
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
        name: str,
    ):
        self._manual_control = manual
        self._automatic_control = automatic
        self._name = name
        self._mode: ControlModes = "manual"
        self._last_mode: ControlModes = "manual"
        self._was_advisory: bool | None = None

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
        is_advisory = sensor_values.mode.is_advisory
        if self._was_advisory and not is_advisory:
            logger.warning(
                "AMCS advisory was disabled for %s (amcs_mode=%s, control_mode=%s); "
                "forcing manual mode and echoing actuated values from AMCS",
                self._name,
                sensor_values.mode.mode.value,
                self._mode,
            )
        self._was_advisory = is_advisory
        if not is_advisory:
            if actuated_control_values is not None:
                self.update_manual_controls(actuated_control_values)
            self._mode = "manual"

        if self._mode == "manual":
            if self._last_mode == "automatic" and actuated_control_values is not None:
                self.update_manual_controls(actuated_control_values)
            control_values, _ = self._manual_control.control(sensor_values)
            self._last_mode = "manual"
            return control_values, self.idle_state()

        if self._last_mode == "manual":
            self._automatic_control.reset()
        control_values, controller_state = self._automatic_control.control(
            sensor_values
        )
        controller_state.automation_mode = AutomationMode(mode="automatic")
        controller_state.manual_values = self.manual_controls
        self._last_mode = "automatic"
        return control_values, controller_state

    def idle_state(self) -> ControllerState:
        """The controller state while the automatic control does not run.

        That is while manual, or without sensor values: the automatic control's
        initial state, with the current parameters and modes.
        """
        _, controller_state = self._automatic_control.initial()
        controller_state.parameters = self._automatic_control.parameters
        controller_state.control_mode = (
            self._automatic_control.mode if self._mode == "automatic" else None
        )
        controller_state.automation_mode = AutomationMode(mode=self._mode)
        controller_state.manual_values = self.manual_controls
        return controller_state

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
    def control_mode(self) -> ControlModes:
        return self._mode

    @property
    def manual_controls(self) -> ControlValues:
        return self._manual_control.controls

    def update_manual_controls(self, values: ControlValues):
        self._manual_control.update_controls(values)
