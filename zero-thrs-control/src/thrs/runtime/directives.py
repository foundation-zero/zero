from collections.abc import Callable
from datetime import datetime

from thrs.orchestration.comms import DirectivesChannels
from thrs.runtime.descriptions.simulation import Mode
from thrs.runtime.loop import ControllableLoop, Request, StatusHook
from thrs.runtime.messages import SimulationStatus, SimulationStatusMessage


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

    def register(self, loop: ControllableLoop) -> StatusHook:
        self._channels.on_status_set(
            lambda msg: loop.request(
                Request(msg.status, msg.playback_rate, msg.pause_at)
            )
        )
        return self.send_status

    async def clear_previous(self):
        await self._channels.send_simulation_status(None)

    async def send_status(self, loop: ControllableLoop, status: SimulationStatus):
        msg = SimulationStatusMessage(
            mode=self._mode.name,
            status=status,
            control_modules=list(self._mode.control_modules),
            simulation_time=self._time_fn(),
            playback_rate=loop.requested.playback_rate,
            pause_at=loop.requested.pause_at,
        )
        await self._channels.send_simulation_status(msg)
