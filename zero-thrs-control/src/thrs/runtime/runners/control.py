import warnings

from thrs.input_output.base import (
    CombinedValues,
)
from thrs.orchestration.comms import ControlChannels
from thrs.orchestration.module import CombinedAlarms, CombinedControl
from thrs.runtime.runners.base import Runner


class ControlRunner[
    S: CombinedValues,
    C: CombinedValues,
    P: CombinedValues,
    M: CombinedValues,
    CS: CombinedValues,
](Runner):
    def __init__(
        self,
        channels: ControlChannels,
        control: CombinedControl,
        alarms: CombinedAlarms,
    ):
        self._channels = channels
        self._control = control
        self._alarms = alarms
        self._control_values, self._controller_state = self._control.initial()

    async def run(self, n_ticks: int) -> None:
        """Run control in a loop for a number of ticks."""
        for _ in range(n_ticks):
            sensor_values = await self._sync_channels_state()
            self._control_values, self._controller_state = self._control.control(
                sensor_values
            )
            await self._send_control_updates()

            self._check_alarms(sensor_values)

    async def _sync_channels_state(self):
        """Synchronize parameters, automation modes, and sensor values."""
        parameters = self._channels.get_parameters()
        if parameters is not None:
            self._control.update_parameters(parameters)

        manual_modes = self._channels.get_automation_modes()
        if manual_modes is not None:
            self._control.update_automation_modes(manual_modes)

        sensor_values = self._channels.get_sensor_values()
        if sensor_values is None:
            sensor_values = CombinedValues(values={})

        await self._channels.send_computed_values(sensor_values)
        return sensor_values

    async def _send_control_updates(self):
        """Send control values, controller state, parameters, control modes, and manual controls to the appropriate channels."""
        await self._channels.send_control_values(self._control_values)
        await self._channels.send_controller_state(self._controller_state)
        await self._channels.send_parameters(self._control.parameters)
        if self._control.mode is not None:
            await self._channels.send_control_modes(self._control.mode)
        await self._channels.send_manual_control(self._control.manual_controls)

    def _check_alarms(self, sensor_values):
        alarms = self._alarms.check(
            sensor_values, self._control_values, self._control.parameters
        )
        if alarms:
            warnings.warn(f"Alarms detected: {alarms}")  # TODO: properly handle alarms
