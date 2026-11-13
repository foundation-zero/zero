from collections.abc import Callable
from datetime import datetime
from functools import partial

from thrs.orchestration.comms import DirectivesChannels
from thrs.runtime.descriptions.simulation import Mode
from thrs.runtime.loop import Loop, LoopHooks, Request
from thrs.runtime.messages import (
    SimulationStatus,
    SimulationStatusMessage,
    SimulationStatusSetMessage,
)


class DirectiveHandler:
    def __init__(self, channels: DirectivesChannels, loop: Loop):
        self._loop = loop
        self._channels = channels

    async def register(self):
        self._channels.on_status_set(self._on_status_set)

    async def _on_status_set(self, msg: SimulationStatusSetMessage):
        await self._loop.request(Request(msg.status, msg.playback_rate, msg.pause_at))


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

    async def send_status(self, loop: Loop, status: SimulationStatus):
        msg = SimulationStatusMessage(
            mode=self._mode.name,
            status=status,
            control_modules=list(self._mode.control_modules),
            simulation_time=self._time_fn(),
            playback_rate=loop.requested.playback_rate,
            pause_at=loop.requested.pause_at,
        )
        await self._channels.send_simulation_status(msg)
