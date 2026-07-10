from thrs.input_output.base import CombinedValues, SimulationInputs, SimulationValues
from thrs.orchestration.comms import ControlChannels, SimulationChannels
from thrs.orchestration.module import CombinedAlarms, CombinedControl
from thrs.orchestration.simulation import Simulation
from thrs.runtime.runners.base import Runner
from thrs.runtime.runners.control import ControlRunner
from thrs.runtime.runners.simulator import SimulationRunner


class LockstepRunner[
    S: CombinedValues,
    I: SimulationInputs,
    O: SimulationValues,
](Runner):
    """Runs a module for a number of ticks."""

    def __init__(
        self,
        control: CombinedControl,
        control_channels: ControlChannels,
        alarms: CombinedAlarms,
        simulation: Simulation[S, CombinedValues, I, O],
        simulation_channels: SimulationChannels[I, O],
    ) -> None:
        self.control_runner = ControlRunner(control, control_channels, alarms)
        self.simulation_runner = SimulationRunner(simulation, simulation_channels)

        self._control_values, _ = control.initial()

    async def run(self, n_ticks: int) -> None:
        """Run simulation and control in lockstep for a number of ticks.
        Retrieve parameters and automation modes from the control channels, and simulation inputs from the simulation channels.
        Send control values to the simulation channels, and sensor values to the control channels.
        """
        for _ in range(n_ticks):
            await self._sync_channels_state()

            sim_result = await self.simulation_runner._execute_simulation_tick(
                self._control_values
            )

            self._control_values = await self.control_runner._execute_control_tick(
                sim_result.sensor_values
            )

    async def _sync_channels_state(self) -> None:
        """Synchronize parameters, automation modes, and simulation inputs."""
        # We are ignoring the sensor values here since we get them from the simulation result
        await self.control_runner._sync_control_channels_state()

        simulation_inputs = (
            self.simulation_runner._simulation_channels.get_simulation_inputs()
        )
        if simulation_inputs is not None:
            self.simulation_runner._simulation.update_simulation_inputs(
                simulation_inputs
            )
