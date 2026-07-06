import warnings
from typing import Protocol

from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
)
from thrs.orchestration.comms import ControlChannels, SimulationChannels
from thrs.orchestration.module import CombinedAlarms, CombinedControl
from thrs.orchestration.simulation import Simulation


class Runner(Protocol):
    async def run(self, n_ticks: int) -> None: ...


class LockstepRunner[
    S: CombinedValues,
    P: CombinedValues,
    M: CombinedValues,
    I: SimulationInputs,
    O: SimulationValues,
    CS: CombinedValues,
](Runner):
    """Runs a module for a number of ticks."""

    def __init__(
        self,
        control: CombinedControl,
        control_channels: ControlChannels,
        simulation_module_name: str,
        simulation: Simulation[S, CombinedValues, I, O],
        simulation_channels: SimulationChannels[I, O],
        alarms: CombinedAlarms,
    ):
        self._control = control
        self._control_channels = control_channels
        self._simulation_module_name = simulation_module_name
        self._simulation = simulation
        self._simulation_channels = simulation_channels
        self._alarms = alarms
        self._control_values, self._controller_state = self._control.initial()

    async def run(self, n_ticks: int) -> None:
        for _ in range(n_ticks):
            parameters = self._control_channels.get_parameters()
            if parameters is not None:
                self._control.update_parameters(parameters)

            manual_modes = self._control_channels.get_automation_modes()
            if manual_modes is not None:
                self._control.update_automation_modes(manual_modes)
            simulation_inputs = self._simulation_channels.get_simulation_inputs()
            if simulation_inputs is not None:
                self._simulation.update_simulation_inputs(simulation_inputs)

            await self._control_channels.send_control_values(self._control_values)

            sim_result = self._simulation.tick(self._control_values)
            await self._control_channels.send_computed_values(sim_result.sensor_values)
            await self._simulation_channels.send_sensor_values(sim_result.sensor_values)
            await self._simulation_channels.send_simulation_inputs(
                sim_result.simulation_inputs
            )
            await self._simulation_channels.send_simulation_outputs(
                sim_result.simulation_outputs
            )

            self._control_values, self._controller_state = self._control.control(
                sim_result.sensor_values
            )
            alarms = self._alarms.check(
                sim_result.sensor_values, self._control_values, self._control.parameters
            )

            await self._control_channels.send_controller_state(self._controller_state)
            await self._control_channels.send_parameters(self._control.parameters)
            if self._control.mode is not None:
                await self._control_channels.send_control_modes(self._control.mode)
            await self._control_channels.send_manual_control(
                self._control.manual_controls
            )

            if alarms:
                warnings.warn(
                    f"Alarms detected: {alarms}"
                )  # TODO: properly handle alarms


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
        for _ in range(n_ticks):
            parameters = self._channels.get_parameters()
            if parameters is not None:
                self._control.update_parameters(parameters)

            manual_modes = self._channels.get_automation_modes()
            if manual_modes is not None:
                self._control.update_automation_modes(manual_modes)

            sensor_values = self._channels.get_sensor_values()
            if sensor_values is None:
                sensor_values = await self._channels.wait_for_sensor_values()

            await self._channels.send_computed_values(sensor_values)

            self._control_values, self._controller_state = self._control.control(
                sensor_values
            )

            await self._channels.send_control_values(self._control_values)
            await self._channels.send_controller_state(self._controller_state)
            await self._channels.send_parameters(self._control.parameters)
            if self._control.mode is not None:
                await self._channels.send_control_modes(self._control.mode)
            await self._channels.send_manual_control(self._control.manual_controls)

            self._check_alarms(sensor_values)

    def _check_alarms(self, sensor_values):
        alarms = self._alarms.check(
            sensor_values, self._control_values, self._control.parameters
        )
        if alarms:
            warnings.warn(f"Alarms detected: {alarms}")  # TODO: properly handle alarms


class SimulationRunner[S: CombinedValues, C, I: SimulationInputs, O: SimulationValues](
    Runner
):
    def __init__(
        self,
        channels: SimulationChannels[I, O],
        simulation: Simulation[S, C, I, O],
    ):
        self._channels = channels
        self._simulation = simulation

    async def run(self, n_ticks: int) -> None:
        for _ in range(n_ticks):
            control_values = self._channels.get_control_values()
            if control_values is None:
                control_values = await self._channels.wait_for_control_values()

            simulation_inputs = self._channels.get_simulation_inputs()
            if simulation_inputs is not None:
                self._simulation.update_simulation_inputs(simulation_inputs)

            sim_result = self._simulation.tick(control_values)
            await self._channels.send_sensor_values(sim_result.sensor_values)
            await self._channels.send_simulation_inputs(sim_result.simulation_inputs)
            await self._channels.send_simulation_outputs(sim_result.simulation_outputs)
