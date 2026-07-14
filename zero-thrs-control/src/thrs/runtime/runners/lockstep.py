from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.orchestration.module import Module
from thrs.orchestration.simulation import SimulationUnit
from thrs.runtime.runners.base import Runner


class LockstepRunner[
    S: CombinedValues,
    I: SimulationInputs,
    O: SimulationValues,
](Runner):
    """Runs a module for a tick."""

    def __init__(
        self,
        control_modules: list[Module],
        simulation_module: SimulationUnit[S, CombinedValues, I, O],
    ) -> None:
        self.control_modules = control_modules
        self.simulation_module = simulation_module

        self._control_values = CombinedValues(
            values={
                module.name: module._control.initial()[0] for module in control_modules
            }
        )

    async def _module_tick(
        self, module: Module, combined_sensor_values: S
    ) -> ThrsValues | None:
        sensor_values = combined_sensor_values.values.get(module.name)

        if sensor_values is None:
            return None

        control_values, controller_state = module.execute_control_tick(sensor_values)

        await module.send_control_updates(
            sensor_values, control_values, controller_state
        )

        return control_values

    async def tick(self) -> None:
        """Run simulation and control in lockstep for a tick.
        Retrieve parameters and automation modes from the control channels, and simulation inputs from the simulation channels.
        Send control values to the simulation channels, and sensor values to the control channels.
        """
        # We are ignoring the sensor values here since we get them from the simulation result
        for module in self.control_modules:
            await module.sync_control_channels_state()

        self.simulation_module.sync_simulation_inputs()

        sim_result = self.simulation_module.execute_simulation_tick(
            self._control_values
        )

        await self.simulation_module.send_simulation_updates(sim_result)

        control_values_map = {
            module.name: control_values
            for module in self.control_modules
            if (
                control_values := await self._module_tick(
                    module, sim_result.sensor_values
                )
            )
        }

        self._control_values = CombinedValues(values=control_values_map)
