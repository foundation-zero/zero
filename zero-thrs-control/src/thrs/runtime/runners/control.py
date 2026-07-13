from thrs.input_output.base import ThrsValues
from thrs.orchestration.module import Module
from thrs.runtime.runners.base import Runner


class ControlRunner[S: ThrsValues](Runner):
    def __init__(
        self,
        control_modules: list[
            Module[S, ThrsValues, ThrsValues, ThrsValues, ThrsValues]
        ],
    ):
        self._modules = control_modules

    async def tick(self) -> None:
        """Run control for a tick."""
        for module in self._modules:
            sensor_values = await module.sync_control_channels_state()

            if sensor_values is None:
                continue
            control_values, controller_state = module.execute_control_tick(
                sensor_values
            )
            await module.send_control_updates(
                sensor_values, control_values, controller_state
            )
