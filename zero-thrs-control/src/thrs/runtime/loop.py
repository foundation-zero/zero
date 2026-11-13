import logging
from asyncio import (
    Queue,
    TaskGroup,
    sleep,
)
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from thrs.runtime.messages import SimulationStatus
from thrs.runtime.runners.base import Runner

logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Request:
    status: SimulationStatus
    playback_rate: float
    pause_at: datetime | None


type Hook = Callable[["Loop"], Awaitable[None]]


@dataclass
class LoopHooks:
    available: Hook
    running: Hook
    stepping: Hook


async def empty_hook(_: Loop):
    pass


EMPTY_HOOKS = LoopHooks(empty_hook, empty_hook, empty_hook)


class Loop:
    """Ticks a runner as requested: paused (available), running at a playback rate,
    or stepping as fast as possible.

    Running and stepping stop at the first tick at or after pause_at, if that is later
    than the time when requested. An earlier pause_at sets no target, so a stale one is
    harmless: running then runs on, and stepping does nothing.
    """

    def __init__(self, tick_duration: timedelta, time_fn: Callable[[], datetime]):
        self._requests = Queue[Request]()
        self._tick_duration = tick_duration
        self._time_fn = time_fn
        self.requested = Request(status="available", playback_rate=1.0, pause_at=None)

    async def loop(self, runner: Runner, hooks: LoopHooks = EMPTY_HOOKS):
        logger.debug("Loop started")

        while True:
            await hooks.available(self)
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
                    await hooks.running(self)
                    while self._requests.empty() and not self._reached(target):
                        async with TaskGroup() as tg:
                            tg.create_task(sleep(sleep_duration))
                            tg.create_task(self._tick_running(runner, hooks))
                case "stepping" if target is not None:
                    await hooks.stepping(self)
                    while self._requests.empty() and not self._reached(target):
                        await runner.tick()
                case "stepping" | "available":
                    pass

    def _reached(self, target: datetime | None) -> bool:
        return target is not None and self._time_fn() >= target

    async def _tick_running(self, runner: Runner, hooks: LoopHooks):
        await runner.tick()
        await hooks.running(self)

    async def request(self, request: Request):
        logger.debug("Loop request: %s", request)
        await self._requests.put(request)

    async def play(self):
        await self.request(Request("running", 1.0, None))
