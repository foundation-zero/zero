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

            await module.tick(sensor_values)
