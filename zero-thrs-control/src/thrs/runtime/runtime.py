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
        """Run the MQTT connector and the loop that ticks the runner."""
        async with TaskGroup() as tg:
            tg.create_task(await self._connector.run())

            tg.create_task(self._loop.loop(self._runner))

    @property
    def runner(self) -> Runner:
        return self._runner
