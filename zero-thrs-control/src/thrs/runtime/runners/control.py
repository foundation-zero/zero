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

    async def run(self) -> None:
        """Run control in a loop for a ticks."""
        for module in self._modules:
            sensor_values = await module.sync_control_channels_state()

            if not sensor_values:
                continue

            control_values, controller_state = module.execute_control_tick(
                sensor_values
            )
            await module.send_control_updates(
                sensor_values, control_values, controller_state
            )
