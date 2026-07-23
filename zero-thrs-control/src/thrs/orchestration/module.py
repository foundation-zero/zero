import logging
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Mapping

from thrs.classes.control import Control
from thrs.classes.machine_state_logger import (
    StateLogger,
)
from thrs.control.manual import ManualControl
from thrs.control.switching import SwitchingControl, SwitchingControlMode
from thrs.input_output.base import ThrsValues

if TYPE_CHECKING:
    from thrs.classes.control import Control
    from thrs.input_output.alarms import Alarm, BaseAlarms
    from thrs.orchestration.comms import ControlChannels

type ModuleClassMap = Mapping[str, type[ThrsValues]]

logger = logging.getLogger(__name__)


class ModuleDescription[
    S: ThrsValues,
    C: ThrsValues,
    P: ThrsValues,
    M: ThrsValues,
    CS: ThrsValues,
]:
    """Description of a module with sensor values, control values, control parameters and control mode models and the control & alarm logic"""

    def __init__(
        self,
        sensor_values_cls: type[S],
        control_values_cls: type[C],
        parameters_cls: type[P],
        control: "Callable[[P, Callable[[], datetime], StateLogger | None], Control[S, C, P, M, CS]]",
        control_mode_cls: type[M],
        controller_state_cls: type[CS],
        alarms: "Callable[[], BaseAlarms[S, C, P]]",
    ):
        self.sensor_values_cls = sensor_values_cls
        self.control_values_cls = control_values_cls
        self.parameters_cls = parameters_cls
        self.control_mode_cls = control_mode_cls
        self.controller_state_cls = controller_state_cls
        self.control = control
        self.alarms = alarms


class Module[
    S: ThrsValues,
    C: ThrsValues,
    P: ThrsValues,
    M: ThrsValues,
    CS: ThrsValues,
]:
    def __init__(
        self,
        name: str,
        control: "Control[S, C, P, M, CS]",
        alarms: "BaseAlarms[S, C, P]",
        channels: "ControlChannels[S, C, P, SwitchingControlMode[M], CS]",
    ):
        self._name = name
        self._control = SwitchingControl(ManualControl(control.initial()[0]), control)
        self._alarms = alarms
        self._channels = channels
        self._active_alarms: dict[str, "Alarm"] = {}

    @property
    def control_state_logger(self) -> StateLogger:
        return self._control.automatic_control.state_logger

    @property
    def name(self):
        return self._name

    async def sync_control_channels_state(self) -> S | None:
        parameters = self._channels.get_parameters()
        if parameters is not None:
            self._control.update_parameters(parameters)

        manual_control_values = self._channels.get_manual_controls()
        if manual_control_values is not None:
            self._control.update_manual_controls(manual_control_values)

        manual_modes = self._channels.get_automation_modes()
        if manual_modes is not None:
            self._control.switch_mode(manual_modes)

        return self._channels.get_sensor_values()

    def execute_control(self, sensor_values: S) -> tuple[C, CS]:
        """Execute a control tick, send control values and evaluate alarms."""

        control_values, controller_state = self._control.control(sensor_values)

        self._check_alarms(sensor_values, control_values)

        return control_values, controller_state

    @StateLogger.log_alarms
    def _check_alarms(self, sensor_values: S, control_values: C) -> list["Alarm"]:
        alarms: list["Alarm"] = self._alarms.check(
            sensor_values,
            control_values,
            self._control.parameters,
        )

        if alarms:
            logger.debug(
                f"Alarms detected: {alarms}"
            )  # TODO: properly handle alarms for AMCS

        return alarms

    async def send_control_updates(
        self, sensor_values: S | None, control_values: C, controller_state: CS
    ) -> None:
        if sensor_values is not None:
            await self._channels.send_computed_values(sensor_values)
        await self._channels.send_control_values(control_values)
        await self._channels.send_controller_state(controller_state)
        await self._channels.send_parameters(self._control.parameters)
        if self._control.mode is not None:
            await self._channels.send_control_modes(self._control.mode)
        await self._channels.send_manual_control(self._control.manual_controls)

    async def tick(self, sensor_values: S | None) -> C:
        if sensor_values is None:
            control_values, controller_state = self._control.initial()
        else:
            control_values, controller_state = self.execute_control(sensor_values)

        await self.send_control_updates(sensor_values, control_values, controller_state)

        return control_values
