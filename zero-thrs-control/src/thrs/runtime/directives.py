from datetime import datetime
from functools import partial
from typing import Callable

from thrs.runtime.descriptions.simulation import Mode
from thrs.runtime.loop import Loop, LoopHooks
from thrs.runtime.messages import (
    Messaging,
    PauseMessage,
    PlayMessage,
    SimulationStatus,
    SimulationStatusMessage,
    StepMessage,
)


class DirectiveHandler:
    def __init__(self, messaging: Messaging, loop: Loop, topic_prefix: str):
        self._loop = loop
        self._messaging = messaging
        self._topic_prefix = topic_prefix

    async def register(self):
        await self._messaging.register(self._topic_prefix, PlayMessage, self._on_play)
        await self._messaging.register(self._topic_prefix, StepMessage, self._on_step)
        await self._messaging.register(self._topic_prefix, PauseMessage, self._on_pause)

    async def _on_play(self, msg: PlayMessage):
        await self._loop.play(msg.playback_rate)

    async def _on_step(self, msg: StepMessage):
        await self._loop.step(msg.seconds)

    async def _on_pause(self, msg: PauseMessage):
        await self._loop.pause()


class DirectiveHandling:
    def __init__(
        self,
        messaging: Messaging,
        mode: Mode,
        time_fn: Callable[[], datetime],
        topic_prefix: str,
    ):
        self._messaging = messaging
        self._mode = mode
        self._time_fn = time_fn
        self._topic_prefix = topic_prefix

    def handler(self, loop: Loop):
        return DirectiveHandler(self._messaging, loop, self._topic_prefix)

    def status_hooks(self) -> LoopHooks:
        return LoopHooks(
            available=partial(self.send_status, status="available"),
            running=partial(self.send_status, status="running"),
            stepping=partial(self.send_status, status="stepping"),
        )

    async def clear_previous(self):
        await self._messaging.clear(self._topic_prefix, [SimulationStatusMessage])

    async def send_status(self, _loop: Loop, status: SimulationStatus):
        msg = SimulationStatusMessage(
            mode=self._mode.name,
            status=status,
            control_modules=self._mode.control_module.modules,
            simulation_time=self._time_fn(),
        )
        await self._messaging.send(self._topic_prefix, msg)

    async def run(self):
        await self._messaging.run()
