from asyncio import Task, create_task, gather, sleep, wait
from datetime import timedelta
from typing import NamedTuple

from thrs.classes.persistence.manager import PersistManager
from thrs.input_output.base import CombinedValues, ThrsValues
from thrs.orchestration.module import Module, ModuleTick
from thrs.orchestration.simulation import SimulationResult, SimulationUnit
from thrs.runtime.loop import Loop, LoopHooks
from thrs.runtime.runners.base import Runner


class LockstepSnapshot(NamedTuple):
    simulation: SimulationResult
    module_ticks: list[tuple[Module, ModuleTick]]


class LockstepRunner[
    S: CombinedValues,
    I: ThrsValues,
    O: ThrsValues,
](Runner):
    """Runs simulation and control in memory for a tick; publishing happens separately."""

    def __init__(
        self,
        control_modules: list[Module],
        simulation_module: SimulationUnit[S, CombinedValues, I, O],
        persistence: PersistManager,
    ) -> None:
        self.control_modules = control_modules
        self.simulation_module = simulation_module
        self._persistence = persistence

        self._control_values = CombinedValues(
            values={
                module.name: module._control.initial()[0] for module in control_modules
            }
        )
        self._unpublished: LockstepSnapshot | None = None

    async def tick(self) -> None:
        """Run simulation and control in lockstep for a tick.
        Retrieve parameters and automation modes from the control channels, and simulation inputs from the simulation channels.
        Pass control values to the simulation, and sensor and actuated control values to the control modules, in memory.
        """
        # We are ignoring the sensor values here since we get them from the simulation result
        for module in self.control_modules:
            await module.sync_control_channels_state()

        self.simulation_module.sync_simulation_inputs()

        sim_result = self.simulation_module.execute_simulation_tick(
            self._control_values
        )

        module_ticks = [
            (
                module,
                module.compute(
                    sim_result.sensor_values.values.get(module.name),
                    sim_result.control_values.values.get(module.name),
                ),
            )
            for module in self.control_modules
        ]

        self._control_values = CombinedValues(
            values={
                module.name: module_tick.control_values
                for module, module_tick in module_ticks
            }
        )
        self._unpublished = LockstepSnapshot(sim_result, module_ticks)

        await self._persistence.persist_all(self.control_modules)

    async def publish(self) -> None:
        """Publish the latest tick, unless it has been published already."""
        snapshot = self._unpublished
        if snapshot is None:
            return
        self._unpublished = None

        # Sent concurrently: each sequential await would let a full tick run in between
        await gather(
            self.simulation_module.send_simulation_updates(snapshot.simulation),
            *(
                module.send_control_updates(module_tick)
                for module, module_tick in snapshot.module_ticks
            ),
        )


class LockstepPublisher:
    """Publishes the lockstep runner's latest tick at a wall-clock interval while the loop plays,
    and once more whenever the loop becomes available again."""

    def __init__(
        self,
        runner: LockstepRunner,
        status_hooks: LoopHooks,
        interval: timedelta,
    ) -> None:
        self._runner = runner
        self._status_hooks = status_hooks
        self._interval = interval
        self._periodic_publish: Task[None] | None = None

    def hooks(self) -> LoopHooks:
        return LoopHooks(
            available=self._on_available,
            running=self._on_running,
            stepping=self._status_hooks.stepping,
        )

    async def _on_running(self, loop: Loop) -> None:
        await self._status_hooks.running(loop)
        self._periodic_publish = create_task(self._publish_periodically(loop))

    async def _on_available(self, loop: Loop) -> None:
        await self._stop_periodic_publish()
        await self._runner.publish()
        await self._status_hooks.available(loop)

    async def _publish_periodically(self, loop: Loop) -> None:
        while True:
            await sleep(self._interval.total_seconds())
            await self._runner.publish()
            await self._status_hooks.running(loop)

    async def _stop_periodic_publish(self) -> None:
        periodic_publish = self._periodic_publish
        if periodic_publish is None:
            return
        self._periodic_publish = None

        periodic_publish.cancel()
        await wait([periodic_publish])
        failure = None if periodic_publish.cancelled() else periodic_publish.exception()
        if failure is not None:
            raise failure
