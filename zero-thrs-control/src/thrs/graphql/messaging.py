from collections.abc import Callable, Coroutine
from typing import Literal, cast

from thrs.control.switching import AutomationMode, SwitchingControlMode
from thrs.input_output.base import ThrsValues
from thrs.orchestration.comms import (
    ControlApiChannels,
    DirectivesApiChannels,
    MqttConnector,
    SimulationApiChannels,
)
from thrs.runtime.messages import SimulationStatusMessage


class ControlMessaging[
    SensorValues: ThrsValues,
    ControlValues: ThrsValues,
    Parameters: ThrsValues,
    Mode: ThrsValues,
    ControllerState: ThrsValues,
]:
    active: bool

    def __init__(
        self,
        channels: ControlApiChannels[
            SensorValues,
            ControlValues,
            Parameters,
            Mode,
            ControllerState,
        ],
    ):
        self.active = False
        self._channels = channels

    async def send_manual_controls(self, control_values: ControlValues):
        if not self.active:
            raise Exception("Cannot send manual controls to inactive module")
        await self._channels.send_manual_values(control_values)

    def wait_for_manual_values(
        self, condition: Callable[[ControlValues], bool], *_args, timeout: float
    ) -> Coroutine[None, None, ControlValues]:
        return cast(
            Coroutine[None, None, ControlValues],
            self._channels.wait_for_manual_values(condition, timeout),
        )

    def wait_for_parameters(
        self, condition: Callable[[Parameters], bool], *_args, timeout: float
    ) -> Coroutine[None, None, Parameters]:
        return cast(
            Coroutine[None, None, Parameters],
            self._channels.wait_for_parameters(condition, timeout),
        )

    @property
    def sensor_values(self) -> SensorValues | None:
        return self._channels.get_sensor_values()

    @property
    def control_values(self) -> ControlValues | None:
        return self._channels.get_control_values() or self._channels.get_manual_values()

    @property
    def controller_state(self) -> ControllerState | None:
        return self._channels.get_controller_state()

    @property
    def parameters(self) -> Parameters | None:
        return self._channels.get_parameters()

    async def set_parameters(self, parameters: Parameters):
        await self._channels.send_parameters(parameters)

    async def set_automation_mode(self, enabled: bool):
        mode = AutomationMode(mode="automatic" if enabled else "manual")
        await self._channels.send_automation_mode(mode)

    def wait_for_control_mode(
        self, automatic: bool, *_args, timeout: float
    ) -> Coroutine[None, None, SwitchingControlMode[Mode]]:
        async def _wait():
            mode = await self._channels.wait_for_control_modes(
                lambda m: bool(getattr(m, "automatic", False)) == automatic,
                timeout,
            )
            return cast(SwitchingControlMode[Mode], mode)

        return _wait()

    @property
    def control_mode(self) -> SwitchingControlMode[Mode] | None:
        mode = self._channels.get_control_modes()
        if mode is None:
            return None
        return cast(SwitchingControlMode[Mode], mode)


class SimulationMessaging:
    def __init__(
        self,
        channels: SimulationApiChannels[ThrsValues, ThrsValues],
    ):
        self._channels = channels

    def wait_for_simulation_inputs(
        self,
        condition: Callable[[ThrsValues], bool],
        *_args,
        timeout: float,
    ) -> Coroutine[None, None, ThrsValues]:
        return self._channels.wait_for_simulation_inputs_where(condition, timeout)

    @property
    def simulation_inputs(self) -> ThrsValues | None:
        return self._channels.get_simulation_inputs()

    @property
    def simulation_outputs(self) -> ThrsValues | None:
        return self._channels.get_simulation_outputs()

    async def set_simulation_inputs(self, inputs: ThrsValues):
        await self._channels.send_simulation_inputs(inputs)


class DirectiveMessaging:
    def __init__(
        self,
        control_modules: list[ControlMessaging],
        simulation: SimulationMessaging,
        directives_channels: DirectivesApiChannels,
        connector: MqttConnector,
    ):
        self._control_modules = control_modules
        self._simulation = simulation
        self._connector = connector
        self._directives_channels = directives_channels

        self._simulation_status: SimulationStatusMessage | None = None
        self._directives_channels.on_simulation_status(self._on_simulation_status)

    async def _on_simulation_status(self, status: SimulationStatusMessage):
        if status == self._simulation_status:
            return

        self._simulation_status = status

        for module in self._control_modules:
            module.active = module._channels.module_name in status.control_modules

    async def run(self) -> Coroutine[None, None, None]:
        return await self._connector.run()

    async def play_simulation(self, playback_rate: float):
        await self._directives_channels.send_play(playback_rate)

    async def pause_simulation(self):
        await self._directives_channels.send_pause()

    async def step_simulation(self, seconds: float):
        await self._directives_channels.send_step(seconds)

    def wait_for_simulation_status(
        self,
        status: Literal["stepping", "running", "available"],
        *_args,
        timeout: float,
    ) -> Coroutine[None, None, SimulationStatusMessage]:
        return self._directives_channels.wait_for_simulation_status_where(
            lambda simulation_status: simulation_status.status == status,
            timeout,
        )

    @property
    def simulation_status(self) -> SimulationStatusMessage | None:
        return self._directives_channels.get_simulation_status()
