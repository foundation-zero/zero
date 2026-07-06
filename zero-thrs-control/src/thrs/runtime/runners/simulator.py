from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
)
from thrs.orchestration.comms import SimulationChannels
from thrs.orchestration.simulation import Simulation, SimulationResult
from thrs.runtime.runners.base import Runner


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
        """Run simulation in a loop for a number of ticks."""
        for _ in range(n_ticks):
            control_values: C = await self._sync_channels_state()

            sim_result: SimulationResult[S, C, I, O] = self._simulation.tick(
                control_values
            )
            await self._send_simulation_updates(sim_result)

    async def _sync_channels_state(self) -> C:
        """Synchronize control values and simulation inputs."""
        control_values = self._channels.get_control_values()
        if control_values is None:
            control_values = await self._channels.wait_for_control_values()

        simulation_inputs = self._channels.get_simulation_inputs()
        if simulation_inputs is not None:
            self._simulation.update_simulation_inputs(simulation_inputs)
        return control_values

    async def _send_simulation_updates(self, sim_result: SimulationResult[S, C, I, O]):
        """Send sensor values, simulation inputs, and simulation outputs to the appropriate channels."""
        await self._channels.send_sensor_values(sim_result.sensor_values)
        await self._channels.send_simulation_inputs(sim_result.simulation_inputs)
        await self._channels.send_simulation_outputs(sim_result.simulation_outputs)
