import logging
from collections.abc import Callable

from thrs.classes.control import Control
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
        create_automatic: Callable[
            [ControlParameters],
            Control[
                SensorValues,
                ControlValues,
                ControlParameters,
                ControlMode,
                ControllerState,
            ],
        ],
        parameters: ControlParameters,
        name: str,
    ):
        """Builds a fresh automatic control from the current parameters each time
        automatic control engages; the manual values start at its initial values,
        until they are set from the first actuated values."""
        self._create_automatic = create_automatic
        self._parameters = parameters
        self._automatic_control = create_automatic(parameters)
        self._manual_controls, _ = self._automatic_control.initial()
        self._name = name
        self._mode: ControlModes = "manual"
        self._last_mode: ControlModes = "manual"
        self._was_advisory = False

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
            self._mode = "manual"

        if self._mode == "manual":
            # Track what was actually actuated: by the AMCS while it is in control,
            # or by our automatic control on the tick we leave it.
            if actuated_control_values is not None and (
                not is_advisory or self._last_mode == "automatic"
            ):
                self.update_manual_controls(actuated_control_values)
            self._last_mode = "manual"
            return self.manual_controls, self.idle_state()

        if self._last_mode == "manual":
            self._automatic_control = self._create_automatic(self._parameters)
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
        initial state, with the current parameters and modes. It has the automatic
        control's mode only once that has run, as a fresh one is built on its first
        tick: until then it has none, as while manual.
        """
        _, controller_state = self._automatic_control.initial()
        controller_state.parameters = self._parameters
        running = self._mode == "automatic" and self._last_mode == "automatic"
        controller_state.control_mode = (
            self._automatic_control.mode if running else None
        )
        controller_state.automation_mode = AutomationMode(mode=self._mode)
        controller_state.manual_values = self.manual_controls
        return controller_state

    def switch_mode(self, mode: AutomationMode):
        self._mode = mode.mode

    def update_parameters(self, parameters: ControlParameters):
        self._parameters = parameters
        self._automatic_control.update_parameters(parameters)

    @property
    def manual_controls(self) -> ControlValues:
        return self._manual_controls

    def update_manual_controls(self, values: ControlValues):
        self._manual_controls = values
