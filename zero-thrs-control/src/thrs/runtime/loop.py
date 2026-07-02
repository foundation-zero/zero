import logging
from asyncio import (
    Queue,
    QueueEmpty,
    TaskGroup,
    sleep,
)
from dataclasses import dataclass
from datetime import timedelta
from typing import Awaitable, Callable

from thrs.runtime.runners import Runner

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class Play:
    playback_rate: float


@dataclass
class Pause:
    pass


@dataclass
class Step:
    seconds: float


type Hook = Callable[["Loop"], Awaitable[None]]


@dataclass
class LoopHooks:
    available: Hook
    running: Hook
    stepping: Hook


async def empty_hook(_: "Loop"):
    pass


EMPTY_HOOKS = LoopHooks(empty_hook, empty_hook, empty_hook)


class Loop:
    def __init__(self, tick_duration: timedelta):
        self._playing = False
        self._playback_rate = 1.0
        self._commands = Queue[Play | Pause | Step]()
        self._tick_duration = tick_duration

    async def loop(self, runner: Runner, hooks: LoopHooks = EMPTY_HOOKS):
        logger.debug("Loop started")

        while True:
            await hooks.available(self)
            result = await self._commands.get()
            match result:
                case Play(playback_rate):
                    self._playing = True
                    self._playback_rate = playback_rate
                    sleep_duration = self._tick_duration.total_seconds() / playback_rate
                    await hooks.running(self)

                    while True:
                        async with TaskGroup() as tg:
                            tg.create_task(sleep(sleep_duration))
                            tg.create_task(runner.run(1))

                        try:
                            command = self._commands.get_nowait()
                            if isinstance(command, Pause):
                                self._playing = False
                                break
                            else:
                                pass  # continue running
                        except QueueEmpty:
                            pass
                case Step(seconds):
                    await hooks.stepping(self)
                    ticks = max(
                        1,
                        int(seconds / self._tick_duration.total_seconds()),
                    )
                    await runner.run(ticks)

    async def play(self, playback_rate: float):
        logger.debug("Loop play requested: %s", playback_rate)
        await self._commands.put(Play(playback_rate))

    async def pause(self):
        logger.debug("Loop pause requested")
        await self._commands.put(Pause())

    async def step(self, seconds: float):
        logger.debug("Loop step requested: %s", seconds)
        await self._commands.put(Step(seconds))
