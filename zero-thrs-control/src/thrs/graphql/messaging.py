from collections.abc import Coroutine
from typing import Any, Literal, cast

from thrs.control.switching import AutomationMode, SwitchingControlMode
from thrs.input_output.base import ThrsValues
from thrs.orchestration.comms import (
    ControlApiChannels,
    DirectivesApiChannels,
    SimulationApiChannels,
)
from thrs.runtime.messages import SimulationStatusMessage

WAIT_TIMEOUT = 5


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

    async def set_manual_control(self, name: str, value: Any) -> ControlValues:
        if not self.active:
            raise Exception("Cannot send manual controls to inactive module")

        control_values = self._channels.get_manual_values()
        if control_values is None:
            raise Exception("No control values available to modify")

        control_values = control_values.model_copy()
        setattr(control_values, name, value)

        expect = self._channels.wait_for_manual_values(
            lambda v: getattr(v, name) == value, timeout_s=WAIT_TIMEOUT
        )
        await self._channels.send_manual_values(control_values)
        try:
            await expect
        except TimeoutError as e:
            raise Exception("Timeout when setting control values") from e

        return control_values

    async def set_parameter(self, name: str, value: Any) -> Parameters:
        parameters = self._channels.get_parameters()
        if parameters is None:
            raise Exception("No parameters available to update")

        parameters = parameters.model_copy()
        setattr(parameters, name, value)

        expect = self._channels.wait_for_parameters(
            lambda parameters: getattr(parameters, name) == value,
            timeout_s=WAIT_TIMEOUT,
        )

        await self._channels.send_parameters(parameters)
        try:
            await expect
        except TimeoutError as e:
            raise Exception("Timeout when setting parameters") from e

        return parameters

    @property
    def sensor_values(self) -> SensorValues | None:
        return self._channels.get_sensor_values()

    @property
    def control_values(self) -> ControlValues | None:
        return self._channels.get_actuated_control_values()

    @property
    def controller_state(self) -> ControllerState | None:
        return self._channels.get_controller_state()

    @property
    def parameters(self) -> Parameters | None:
        return self._channels.get_parameters()

    async def set_automation_mode(self, enabled: bool) -> bool:
        mode = AutomationMode(mode="automatic" if enabled else "manual")
        await self._channels.send_automation_mode(mode)

        try:
            await self._channels.wait_for_control_modes(
                lambda m: bool(getattr(m, "automatic", False)) == enabled,
                timeout_s=WAIT_TIMEOUT,
            )
        except TimeoutError as e:
            raise Exception("Timeout when setting automation mode") from e
        return enabled

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

    @property
    def simulation_inputs(self) -> ThrsValues | None:
        return self._channels.get_simulation_inputs()

    @property
    def simulation_outputs(self) -> ThrsValues | None:
        return self._channels.get_simulation_outputs()

    async def set_simulation_input(self, name: str, value: Any) -> ThrsValues:
        inputs = self._channels.get_simulation_inputs()
        if inputs is None:
            raise Exception("No simulation inputs available to modify")

        inputs = inputs.model_copy()
        setattr(inputs, name, value)

        expect = self._channels.wait_for_simulation_inputs(
            lambda inputs: getattr(inputs, name) == value,
            timeout_s=WAIT_TIMEOUT,
        )
        await self._channels.send_simulation_inputs(inputs)
        try:
            await expect
        except TimeoutError as e:
            raise Exception("Timeout when setting simulation inputs") from e
        return inputs


class DirectiveMessaging:
    def __init__(
        self,
        control_modules: list[ControlMessaging],
        directives_channels: DirectivesApiChannels,
    ):
        self._control_modules = control_modules
        self._directives_channels = directives_channels

        self._simulation_status: SimulationStatusMessage | None = None
        self._directives_channels.on_simulation_status(self._on_simulation_status)

    async def _on_simulation_status(self, status: SimulationStatusMessage):
        if status == self._simulation_status:
            return

        self._simulation_status = status

        for module in self._control_modules:
            module.active = module._channels.module_name in status.control_modules

    async def play_simulation(self, playback_rate: float):
        simulation_status = self._directives_channels.get_simulation_status()
        if simulation_status is None:
            raise Exception("No simulation status available, cannot play")
        if simulation_status.status not in ("available", "running"):
            raise Exception("Can only play an available or running simulation")

        expect_status = self._wait_for_simulation_status(
            "running", timeout=WAIT_TIMEOUT
        )
        await self._directives_channels.send_play(playback_rate)
        await expect_status

    async def pause_simulation(self):
        simulation_status = self._directives_channels.get_simulation_status()
        if simulation_status is None:
            raise Exception("No simulation status available, cannot pause")
        if simulation_status.status != "running":
            raise Exception("Can only pause a running simulation")

        expect_status = self._wait_for_simulation_status(
            "available", timeout=WAIT_TIMEOUT
        )
        await self._directives_channels.send_pause()
        await expect_status

    async def step_simulation(self, seconds: float):
        simulation_status = self._directives_channels.get_simulation_status()
        if simulation_status is None:
            raise Exception("No simulation status available, cannot step")
        if simulation_status.status != "available":
            raise Exception("Can only step an available simulation")

        expect_status = self._wait_for_simulation_status(
            "stepping", timeout=WAIT_TIMEOUT
        )
        await self._directives_channels.send_step(seconds)
        await expect_status

    def _wait_for_simulation_status(
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
