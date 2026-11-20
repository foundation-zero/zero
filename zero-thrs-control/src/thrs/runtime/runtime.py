from asyncio import TaskGroup

from thrs.orchestration.comms import MqttConnector
from thrs.runtime.loop import Loop
from thrs.runtime.runners.base import Runner


class Runtime:
    def __init__(
        self,
        loop: Loop,
        runner: Runner,
        connector: MqttConnector,
    ):
        self._loop = loop
        self._runner = runner
        self._connector = connector

    async def start(self):
        """Start the runtime, including the loop and any directive handling if present. Hooks are used to send status messages for directive handling."""
        async with TaskGroup() as tg:
            tg.create_task(await self._connector.run())

            tg.create_task(self._loop.loop(self._runner))

    async def clear_previous(self):
        await self._loop.clear_previous()

    async def play(self):
        await self._loop.play()
