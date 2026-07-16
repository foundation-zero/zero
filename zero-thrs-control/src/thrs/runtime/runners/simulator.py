from thrs.input_output.base import CombinedValues, SimulationInputs, SimulationValues
from thrs.orchestration.simulation import SimulationUnit
from thrs.runtime.liveness import Liveness
from thrs.runtime.runners.base import Runner


class SimulationRunner[
    C: CombinedValues,
    I: SimulationInputs,
    O: SimulationValues,
](Runner):
    def __init__(
        self,
        simulation_module: SimulationUnit[CombinedValues, C, I, O],
        liveness: Liveness,
    ) -> None:
        self._simulation_module = simulation_module
        self._liveness = liveness

    async def tick(self) -> None:
        """Run simulation for a tick."""
        self._liveness.signal()

        control_values = await self._simulation_module.sync_simulation_channels_state()

        sim_result = self._simulation_module.execute_simulation_tick(control_values)

        await self._simulation_module.send_simulation_updates(sim_result)
