from thrs.classes.persistence.manager import PersistManager
from thrs.input_output.base import ThrsValues
from thrs.input_output.sensor_values import AmcsModeSensorValues
from thrs.orchestration.module import Module
from thrs.runtime.liveness import Liveness
from thrs.runtime.runners.base import Runner


class ControlRunner[S: AmcsModeSensorValues](Runner):
    def __init__(
        self,
        control_modules: list[
            Module[S, ThrsValues, ThrsValues, ThrsValues, ThrsValues]
        ],
        liveness: Liveness,
        persistence: PersistManager,
    ):
        self._modules = control_modules
        self._liveness = liveness
        self._persistence = persistence

    async def tick(self) -> None:
        """Run control for a tick."""
        self._liveness.signal()

        for module in self._modules:
            sensor_values = await module.sync_control_channels_state()

            await module.tick(sensor_values)

            await self._persistence.persist(module)
