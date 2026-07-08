import warnings
from datetime import datetime
from typing import Callable, cast

from thrs.control.manual import ManualControl
from thrs.control.switching import AutomationMode, SwitchingControl
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import ThrsValues
from thrs.orchestration.comms import ControlChannels
from thrs.orchestration.module import ModuleDescription
from thrs.runtime.runners.base import Runner


class ControlRunner(Runner):
    def __init__(
        self,
        control_modules: dict[str, ModuleDescription],
        time_fn: Callable[[], datetime],
        channels: dict[str, ControlChannels],
    ):
        parameters = {
            module_name: module.parameters_cls()
            for module_name, module in control_modules.items()
        }

        self._modules = control_modules
        self._controls: dict[str, SwitchingControl] = {
            module_name: SwitchingControl(
                ManualControl(control.initial()[0], time_fn),
                control,
            )
            for module_name, module in control_modules.items()
            if module_name in parameters
            and (control := module.control(parameters[module_name], time_fn))
        }
        self._control_channels = channels
        self._alarms: dict[str, BaseAlarms] = {
            module_name: module.alarms()
            for module_name, module in control_modules.items()
        }

    async def run(self, n_ticks: int) -> None:
        """Run control in a loop for a number of ticks."""
        for _ in range(n_ticks):
            for name in self._controls:
                sensor_values = await self._sync_control_channels_state(name)
                await self._execute_control_tick(name, sensor_values)

    async def _sync_control_channels_state(self, name: str) -> ThrsValues | None:
        """Synchronize parameters, automation modes, and sensor values."""
        parameters = self._control_channels[name].get_parameters()
        if parameters is not None:
            self._controls[name].update_parameters(parameters)

        manual_control_values = self._control_channels[name].get_manual_controls()
        if manual_control_values is not None:
            self._controls[name].update_manual_controls(manual_control_values)

        manual_modes = self._control_channels[name].get_automation_modes()
        if manual_modes is not None:
            expected_mode = cast(AutomationMode, manual_modes)
            self._controls[name].switch_mode(expected_mode)

        return self._control_channels[name].get_sensor_values()

    async def _execute_control_tick(
        self, name: str, sensor_values: ThrsValues | None
    ) -> ThrsValues | None:
        """Execute a control tick, send control values and evaluate alarms."""
        if sensor_values is None:
            return None

        control_values, controller_state = self._controls[name].control(sensor_values)

        await self._send_control_updates(
            name, sensor_values, control_values, controller_state
        )

        self._check_alarms(name, sensor_values, control_values)

        return control_values

    def _check_alarms(
        self,
        name: str,
        sensor_values: ThrsValues,
        control_values: ThrsValues,
    ) -> None:
        alarms = self._alarms[name].check(
            sensor_values,
            control_values,
            self._controls[name].parameters,
        )

        if alarms:
            warnings.warn(f"Alarms detected: {alarms}")  # TODO: properly handle alarms

    async def _send_control_updates(
        self,
        name: str,
        sensor_values: ThrsValues,
        control_values: ThrsValues,
        controller_state: ThrsValues,
    ) -> None:
        """Send control values, controller state, parameters, control modes, and manual controls to the control channels."""
        await self._control_channels[name].send_computed_values(sensor_values)
        await self._control_channels[name].send_control_values(control_values)
        await self._control_channels[name].send_controller_state(controller_state)
        await self._control_channels[name].send_parameters(
            self._controls[name].parameters
        )
        if self._controls[name].mode is not None:
            await self._control_channels[name].send_control_modes(
                self._controls[name].mode
            )
        await self._control_channels[name].send_manual_control(
            self._controls[name].manual_controls
        )
