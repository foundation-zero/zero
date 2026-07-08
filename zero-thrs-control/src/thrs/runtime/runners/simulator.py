from thrs.input_output.base import CombinedValues, SimulationInputs, SimulationValues
from thrs.orchestration.comms import SimulationChannels
from thrs.orchestration.simulation import Simulation, SimulationResult
from thrs.runtime.runners.base import Runner


class SimulationRunner[
    S: CombinedValues,
    I: SimulationInputs,
    O: SimulationValues,
](Runner):
    def __init__(
        self,
        simulation: Simulation[S, CombinedValues, I, O],
        channels: SimulationChannels[I, O],
    ) -> None:
        self._simulation = simulation
        self._simulation_channels = channels

    async def run(self, n_ticks: int) -> None:
        """Run simulation in a loop for a number of ticks."""
        for _ in range(n_ticks):
            control_values = await self._sync_simulation_channels_state()

            await self._execute_simulation_tick(control_values)

    async def _sync_simulation_channels_state(self) -> CombinedValues:
        """Synchronize control values and simulation inputs."""

        simulation_inputs = self._simulation_channels.get_simulation_inputs()
        if simulation_inputs is not None:
            self._simulation.update_simulation_inputs(simulation_inputs)

        control_values = self._simulation_channels.get_control_values()
        if control_values is None:
            control_values = await self._simulation_channels.wait_for_control_values()
        return control_values

    async def _execute_simulation_tick(
        self, control_values: CombinedValues
    ) -> SimulationResult[S, CombinedValues, I, O]:
        """Execute a simulation tick and send the results to the appropriate channels."""
        sim_result = self._simulation.tick(control_values)

        await self._send_simulation_updates(sim_result)

        return sim_result

    async def _send_simulation_updates(
        self, sim_result: SimulationResult[S, CombinedValues, I, O]
    ) -> None:
        """Send sensor values, simulation inputs, and simulation outputs to the appropriate channels."""
        await self._simulation_channels.send_sensor_values(sim_result.sensor_values)
        await self._simulation_channels.send_simulation_inputs(
            sim_result.simulation_inputs
        )
        await self._simulation_channels.send_simulation_outputs(
            sim_result.simulation_outputs
        )
