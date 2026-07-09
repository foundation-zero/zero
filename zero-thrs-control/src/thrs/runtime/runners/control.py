import warnings
from typing import cast

from thrs.input_output.base import CombinedValues
from thrs.orchestration.comms import ControlChannels
from thrs.orchestration.module import CombinedAlarms, CombinedControl
from thrs.runtime.runners.base import Runner


class ControlRunner[
    S: CombinedValues,
](Runner):
    def __init__(
        self,
        control: CombinedControl,
        channels: ControlChannels,
        alarms: CombinedAlarms,
    ):
        self._channels = channels
        self._control = control
        self._control_channels = channels
        self._alarms = alarms

    async def run(self, n_ticks: int) -> None:
        """Run control in a loop for a number of ticks."""
        for _ in range(n_ticks):
            sensor_values = await self._sync_control_channels_state()
            await self._execute_control_tick(sensor_values)

    async def _sync_control_channels_state(self) -> S:
        """Synchronize parameters, automation modes, and sensor values."""
        parameters = self._control_channels.get_parameters()
        if parameters is not None:
            self._control.update_parameters(parameters)

        manual_control_values = self._control_channels.get_manual_controls()
        if manual_control_values is not None:
            self._control.update_manual_controls(manual_control_values)

        manual_modes = self._control_channels.get_automation_modes()
        if manual_modes is not None:
            self._control.update_automation_modes(manual_modes)

        sensor_values = self._control_channels.get_sensor_values()
        if sensor_values is None:
            sensor_values = cast(S, CombinedValues(values={}))

        return sensor_values

    async def _execute_control_tick(self, sensor_values: S) -> CombinedValues:
        """Execute a control tick, send control values and evaluate alarms."""
        control_values, controller_state = self._control.control(sensor_values)

        await self._send_control_updates(
            sensor_values, control_values, controller_state
        )

        self._check_alarms(sensor_values, control_values)

        return control_values

    def _check_alarms(self, sensor_values: S, control_values: CombinedValues) -> None:
        alarms = self._alarms.check(
            sensor_values, control_values, self._control.parameters
        )

        if alarms:
            warnings.warn(f"Alarms detected: {alarms}")  # TODO: properly handle alarms

    async def _send_control_updates(
        self,
        sensor_values: S,
        control_values: CombinedValues,
        controller_state: CombinedValues,
    ) -> None:
        """Send control values, controller state, parameters, control modes, and manual controls to the control channels."""
        await self._control_channels.send_computed_values(sensor_values)
        await self._control_channels.send_control_values(control_values)
        await self._control_channels.send_controller_state(controller_state)
        await self._control_channels.send_parameters(self._control.parameters)
        if self._control.mode is not None:
            await self._control_channels.send_control_modes(self._control.mode)
        await self._control_channels.send_manual_control(self._control.manual_controls)
