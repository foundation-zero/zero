from datetime import datetime
from functools import partial
from typing import Callable

from thrs.orchestration.comms import DirectivesChannels
from thrs.runtime.descriptions.simulation import Mode
from thrs.runtime.loop import Loop, LoopHooks
from thrs.runtime.messages import (
    PauseMessage,
    PlayMessage,
    SimulationStatus,
    SimulationStatusMessage,
    StepMessage,
)


class DirectiveHandler:
    def __init__(self, channels: DirectivesChannels, loop: Loop):
        self._loop = loop
        self._channels = channels

    async def register(self):
        self._channels.on_play(self._on_play)
        self._channels.on_step(self._on_step)
        self._channels.on_pause(self._on_pause)

    async def _on_play(self, msg: PlayMessage):
        await self._loop.play(msg.playback_rate)

    async def _on_step(self, msg: StepMessage):
        await self._loop.step(msg.seconds)

    async def _on_pause(self, msg: PauseMessage):
        await self._loop.pause()


class DirectiveHandling:
    def __init__(
        self,
        channels: DirectivesChannels,
        mode: Mode,
        time_fn: Callable[[], datetime],
    ):
        self._channels = channels
        self._mode = mode
        self._time_fn = time_fn

    def handler(self, loop: Loop):
        return DirectiveHandler(self._channels, loop)

    def status_hooks(self) -> LoopHooks:
        return LoopHooks(
            available=partial(self.send_status, status="available"),
            running=partial(self.send_status, status="running"),
            stepping=partial(self.send_status, status="stepping"),
        )

    async def clear_previous(self):
        await self._channels.clear_simulation_status()

    async def send_status(self, _loop: Loop, status: SimulationStatus):
        msg = SimulationStatusMessage(
            mode=self._mode.name,
            status=status,
            control_modules=self._mode.control_module.modules,
            simulation_time=self._time_fn(),
        )
        await self._channels.send_simulation_status(msg)

    async def run(self):
        return
