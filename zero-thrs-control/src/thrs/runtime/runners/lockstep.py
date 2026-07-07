import warnings

from thrs.input_output.alarms import Alarm
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
)
from thrs.orchestration.comms import ControlChannels, SimulationChannels
from thrs.orchestration.module import CombinedAlarms, CombinedControl
from thrs.orchestration.simulation import Simulation, SimulationResult
from thrs.runtime.runners.base import Runner


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
        simulation: Simulation[S, CombinedValues, I, O],
        simulation_channels: SimulationChannels[I, O],
        alarms: CombinedAlarms,
    ) -> None:
        self._control = control
        self._control_channels = control_channels
        self._simulation = simulation
        self._simulation_channels = simulation_channels
        self._alarms = alarms
        self._control_values, self._controller_state = self._control.initial()

    async def run(self, n_ticks: int) -> None:
        """Run simulation and control in lockstep for a number of ticks.
        Retrieve parameters and automation modes from the control channels, and simulation inputs from the simulation channels.
        Send control values to the simulation channels, and sensor values to the control channels.
        """
        for _ in range(n_ticks):
            await self._sync_channels_state()
            sim_result = await self._execute_simulation_tick()
            await self._execute_control_tick(sim_result)

    async def _sync_channels_state(self) -> None:
        """Synchronize parameters, automation modes, and simulation inputs."""
        parameters = self._control_channels.get_parameters()
        if parameters is not None:
            self._control.update_parameters(parameters)

        manual_modes = self._control_channels.get_automation_modes()
        if manual_modes is not None:
            self._control.update_automation_modes(manual_modes)

        simulation_inputs = self._simulation_channels.get_simulation_inputs()
        if simulation_inputs is not None:
            self._simulation.update_simulation_inputs(
                simulation_inputs
            )  # TODO: properly handle alarms

        await self._control_channels.send_control_values(self._control_values)

    async def _execute_simulation_tick(
        self,
    ) -> SimulationResult[S, CombinedValues, I, O]:
        """Execute a simulation tick and send the results to the appropriate channels."""

        # Control values are not retrieved, since we are in lockstep and derived from the previous control tick.
        sim_result: SimulationResult[S, CombinedValues, I, O] = self._simulation.tick(
            self._control_values
        )
        await self._control_channels.send_computed_values(sim_result.sensor_values)
        await self._simulation_channels.send_sensor_values(sim_result.sensor_values)
        await self._simulation_channels.send_simulation_inputs(
            sim_result.simulation_inputs
        )
        await self._simulation_channels.send_simulation_outputs(
            sim_result.simulation_outputs
        )

        return sim_result

    async def _execute_control_tick(
        self,
        sim_result: SimulationResult[S, CombinedValues, I, O],
    ) -> None:
        """Execute a control tick, send control values and evaluate alarms."""
        self._control_values, self._controller_state = self._control.control(
            sim_result.sensor_values
        )

        alarms = self._check_alarms(sim_result)
        await self._send_control_updates()
        self._evaluate_alarms(alarms)

    def _check_alarms(
        self,
        sim_result: SimulationResult[S, CombinedValues, I, O],
    ) -> list[Alarm]:
        alarms: list[Alarm] = self._alarms.check(
            sim_result.sensor_values, self._control_values, self._control.parameters
        )

        return alarms

    async def _send_control_updates(self) -> None:
        """Send control values, controller state, parameters, control modes, and manual controls to the control channels."""
        await self._control_channels.send_controller_state(self._controller_state)
        await self._control_channels.send_parameters(self._control.parameters)
        if self._control.mode is not None:
            await self._control_channels.send_control_modes(self._control.mode)
        await self._control_channels.send_manual_control(self._control.manual_controls)

    def _evaluate_alarms(self, alarms: list[Alarm]) -> None:
        if alarms:
            warnings.warn(f"Alarms detected: {alarms}")
