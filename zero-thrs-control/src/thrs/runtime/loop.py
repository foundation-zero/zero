import logging
from asyncio import (
    Queue,
    TaskGroup,
    sleep,
)
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Protocol

from thrs.runtime.messages import SimulationStatus
from thrs.runtime.runners.base import Runner

if TYPE_CHECKING:
    from thrs.runtime.directives import DirectiveHandling


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Request:
    status: SimulationStatus
    playback_rate: float
    pause_at: datetime | None


type StatusHook = Callable[["ControllableLoop", SimulationStatus], Awaitable[None]]


async def _empty_hook(_: Loop, _status: SimulationStatus):
    pass


class Loop(Protocol):
    async def loop(self, runner: Runner): ...
    async def play(self): ...
    async def clear_previous(self): ...


class RealtimeLoop(Loop):
    """Ticks a runner at realtime speed."""

    async def loop(self, runner: Runner):
        logger.debug("Loop started")

        sleep_duration = 1
        while True:
            async with TaskGroup() as tg:
                tg.create_task(sleep(sleep_duration))
                tg.create_task(runner.tick())

    async def play(self):
        pass

    async def clear_previous(self):
        pass


class ControllableLoop(Loop):
    """Ticks a runner as requested: paused (available), running at a playback rate,
    or stepping as fast as possible.

    Running and stepping stop at the first tick at or after pause_at, if that is later
    than the time when requested. An earlier pause_at sets no target, so a stale one is
    harmless: running then runs on, and stepping does nothing.
    """

    def __init__(
        self,
        tick_duration: timedelta,
        time_fn: Callable[[], datetime],
        directive_handling: DirectiveHandling | None = None,
    ):
        self._requests = Queue[Request]()
        self._tick_duration = tick_duration
        self._time_fn = time_fn
        self.requested = Request(status="available", playback_rate=1.0, pause_at=None)
        self._directive_handling = directive_handling
        self._status_hook: StatusHook = (
            directive_handling.register(self)
            if directive_handling is not None
            else _empty_hook
        )

    async def loop(self, runner: Runner):
        logger.debug("Loop started")

        hook = self._status_hook
        while True:
            await hook(self, "available")
            self.requested = await self._requests.get()
            pause_at = self.requested.pause_at
            target = (
                pause_at
                if pause_at is not None and pause_at > self._time_fn()
                else None
            )

            match self.requested.status:
                case "running":
                    sleep_duration = (
                        self._tick_duration.total_seconds()
                        / self.requested.playback_rate
                    )
                    await hook(self, "running")
                    while self._requests.empty() and not self._reached(target):
                        async with TaskGroup() as tg:
                            tg.create_task(sleep(sleep_duration))
                            tg.create_task(self._tick_running(runner, hook))
                case "stepping" if target is not None:
                    await hook(self, "stepping")
                    while self._requests.empty() and not self._reached(target):
                        await runner.tick()
                case "stepping" | "available":
                    pass

    def _reached(self, target: datetime | None) -> bool:
        return target is not None and self._time_fn() >= target

    async def _tick_running(self, runner: Runner, hook: StatusHook):
        await runner.tick()
        await hook(self, "running")

    def request(self, request: Request):
        logger.debug("Loop request: %s", request)
        self._requests.put_nowait(request)

    async def play(self):
        self.request(Request("running", 1.0, None))

    async def clear_previous(self):
        if self._directive_handling is not None:
            await self._directive_handling.clear_previous()
