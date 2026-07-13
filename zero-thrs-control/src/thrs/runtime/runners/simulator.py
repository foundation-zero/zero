from thrs.input_output.base import CombinedValues, SimulationInputs, SimulationValues
from thrs.orchestration.simulation import SimulationUnit
from thrs.runtime.runners.base import Runner


class SimulationRunner[
    C: CombinedValues,
    I: SimulationInputs,
    O: SimulationValues,
](Runner):
    def __init__(
        self, simulation_module: SimulationUnit[CombinedValues, C, I, O]
    ) -> None:
        self.simulation_module = simulation_module

    async def tick(self) -> None:
        """Run simulation for a tick."""
        control_values = await self.simulation_module.sync_simulation_channels_state()

        sim_result = self.simulation_module.execute_simulation_tick(control_values)

        await self.simulation_module.send_simulation_updates(sim_result)
