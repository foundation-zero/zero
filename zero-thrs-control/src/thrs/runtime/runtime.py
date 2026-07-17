from asyncio import TaskGroup
from datetime import timedelta

from thrs.orchestration.comms import MqttConnector
from thrs.runtime.directives import DirectiveHandling
from thrs.runtime.loop import EMPTY_HOOKS, Loop
from thrs.runtime.runners.base import Runner


class Runtime:
    def __init__(
        self,
        runner: Runner,
        connector: MqttConnector,
        tick_duration: timedelta,
        directive_handling: DirectiveHandling | None = None,
    ):
        self._loop = Loop(tick_duration)
        self._runner = runner
        self._directive_handling = directive_handling
        self._connector = connector

    async def start(self):
        """Start the runtime, including the loop and any directive handling if present. Hooks are used to send status messages for directive handling."""
        async with TaskGroup() as tg:
            tg.create_task(await self._connector.run())

            if self._directive_handling is not None:
                await self._directive_handling.handler(self._loop).register()

            status_hooks = (
                self._directive_handling.status_hooks()
                if self._directive_handling is not None
                else EMPTY_HOOKS
            )

            tg.create_task(
                self._loop.loop(
                    self._runner,
                    status_hooks,
                )
            )

    async def clear_previous(self):
        if self._directive_handling is not None:
            await self._directive_handling.clear_previous()

    @property
    def loop(self) -> Loop:
        return self._loop

    @property
    def runner(self) -> Runner:
        return self._runner
