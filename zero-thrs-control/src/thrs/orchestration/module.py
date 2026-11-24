import logging
from collections.abc import Callable, Mapping
from datetime import datetime
from typing import TYPE_CHECKING

from thrs.classes.control import Control
from thrs.control.state import AutomationMode, ControlModes, ControlState
from thrs.control.switching import Switching
from thrs.input_output.base import ThrsValues
from thrs.input_output.definitions.system import AmcsExternalAvailable
from thrs.input_output.root_types import AmcsModeSensorValues, AmcsWatchdogControlValues

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
    """Description of a module with sensor values, control values, control parameters and controller state models and the control & alarm logic"""

    def __init__(
        self,
        sensor_values_cls: type[S],
        control_values_cls: type[C],
        parameters_cls: type[P],
        control: Callable[[P, Callable[[], datetime]], Control[S, C, P, M, CS]],
        controller_state_cls: type[CS],
        alarms: Callable[[], BaseAlarms[S, C, CS]],
    ):
        self.sensor_values_cls = sensor_values_cls
        self.control_values_cls = control_values_cls
        self.parameters_cls = parameters_cls
        self.controller_state_cls = controller_state_cls
        self.control = control
        self.alarms = alarms


class Module[
    S: AmcsModeSensorValues,
    C: AmcsWatchdogControlValues,
    P: ThrsValues,
    M: ThrsValues,
    CS: ControlState,
]:
    def __init__(
        self,
        name: str,
        description: ModuleDescription[S, C, P, M, CS],
        channels: ControlChannels[S, C, P, M, CS],
        time_fn: Callable[[], datetime],
        parameters: P | None = None,
        automation_mode: ControlModes = "manual",
    ):
        """Starts with the given parameters, or the defaults, and automation mode."""
        self._name = name
        control = description.control(
            parameters if parameters is not None else description.parameters_cls(),
            time_fn,
        )
        self._control = Switching(control.initial()[0], control, name=name)
        self._control.switch_mode(AutomationMode(mode=automation_mode))
        self._alarms = description.alarms()
        self._channels = channels

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

        control_values_set = self._channels.get_control_values_set()
        if control_values_set is not None:
            self._control.update_manual_controls(control_values_set)

        manual_modes = self._channels.get_automation_modes()
        if manual_modes is not None:
            self._control.switch_mode(manual_modes)

        return self._channels.get_sensor_values()

    def execute_control(self, sensor_values: S) -> tuple[C, CS]:
        """Execute a control tick, send control values and evaluate alarms."""
        control_values, controller_state = self._control.control(
            sensor_values, self._channels.get_actuated_control_values()
        )

        self._check_alarms(sensor_values, control_values, controller_state)

        return control_values, controller_state

    def set_automation_mode(self, mode: AutomationMode) -> None:
        self._control.switch_mode(mode)

    def _check_alarms(
        self, sensor_values: S, control_values: C, controller_state: CS
    ) -> list[Alarm]:
        alarms: list[Alarm] = self._alarms.check(
            sensor_values,
            control_values,
            controller_state,
        )

        if alarms:
            logger.debug(
                "Alarms detected: %s", alarms
            )  # TODO: properly handle alarms for AMCS

        return alarms

    async def send_control_updates(
        self, sensor_values: S | None, control_values: C, controller_state: CS
    ) -> None:
        if sensor_values is not None:
            await self._channels.send_computed_values(sensor_values)
        await self._channels.send_control_values(control_values)
        await self._channels.send_controller_state(controller_state)
        actuated_control_values = self._channels.get_actuated_control_values()
        if actuated_control_values is not None:
            await self._channels.send_actuated_control_values(actuated_control_values)

    async def tick(self, sensor_values: S | None) -> tuple[C, CS]:
        if sensor_values is None:
            logger.warning(
                "Module %s has no sensor values - sending last known manual control values",
                self._name,
            )
            control_values = self._control.manual_controls
            controller_state = self._control.idle_state()
        else:
            control_values, controller_state = self.execute_control(sensor_values)

        # Update amcs watchdog timestamp
        control_values.external_available = AmcsExternalAvailable()

        await self.send_control_updates(sensor_values, control_values, controller_state)

        return control_values, controller_state
