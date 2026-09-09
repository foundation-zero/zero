import logging
from collections.abc import Callable
from datetime import datetime
from typing import Literal

from thrs.classes.control import Control
from thrs.classes.machine_state_logger import StateLogger
from thrs.control.manual import ManualControl
from thrs.input_output.base import ThrsValues
from thrs.input_output.sensor_values import AmcsModeSensorValues

type ControlModes = Literal["manual", "automatic"]

logger = logging.getLogger(__name__)


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
        name: str,
        automatic_factory: Callable[
            [ControlParameters, Callable[[], datetime], StateLogger],
            Control[
                SensorValues,
                ControlValues,
                ControlParameters,
                ControlMode,
                ControllerState,
            ],
        ],
        time_fn: Callable[[], datetime],
        state_logger: StateLogger,
    ):
        self._manual_control = manual
        self._automatic_control = automatic
        self._automatic_factory = automatic_factory
        self._time_fn = time_fn
        self._name = name
        self._mode: ControlModes = "manual"
        self._last_mode: ControlModes = "manual"
        self._was_advisory: bool | None = None
        self.state_logger: StateLogger = state_logger

    def _rebuild_automatic(self) -> None:
        parameters = self._automatic_control.parameters
        self._automatic_control = self._automatic_factory(
            parameters, self._time_fn, self.state_logger
        )

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

        if self.control_mode == "manual":
            control_values, _ = self._manual_control.control(sensor_values)
            _, controller_state = self._automatic_control.initial()
            self._last_mode = "manual"
            return control_values, controller_state
        if self._last_mode == "manual":
            self._rebuild_automatic()
        control_values, controller_state = self._automatic_control.control(
            sensor_values
        )
        self._last_mode = "automatic"
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
