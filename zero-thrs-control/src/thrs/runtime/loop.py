from asyncio import FIRST_COMPLETED, Queue, TaskGroup, create_task, sleep, wait
from dataclasses import dataclass
from datetime import timedelta
from typing import Awaitable, Callable, Coroutine, Never, assert_never, cast

from thrs.runtime.runners import Runner


@dataclass
class First[T]:
    result: T


@dataclass
class Second[T]:
    result: T


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
        self._pauses = Queue()
        self._plays: Queue[float] = Queue()
        self._steps: Queue[float] = Queue()
        self._tick_duration = tick_duration

    async def loop(self, runner: Runner, hooks: LoopHooks = EMPTY_HOOKS):
        while True:
            await hooks.available(self)
            result = await self.wait_either(self._plays.get(), self._steps.get())
            match result:
                case First(playback_rate):
                    self._playing = True
                    self._playback_rate = playback_rate
                    sleep_duration = self._tick_duration.total_seconds() / playback_rate
                    await hooks.running(self)
                    while self._pauses.empty():
                        async with TaskGroup() as tg:
                            tg.create_task(sleep(sleep_duration))
                            tg.create_task(runner.run(1))
                    self._pauses.get_nowait()
                    self._playing = False
                case Second(seconds):
                    await hooks.stepping(self)
                    ticks = max(
                        1,
                        int(seconds / self._tick_duration.total_seconds()),
                    )
                    await runner.run(ticks)

    async def play(self, playback_rate: float):
        await self._plays.put(playback_rate)

    async def pause(self):
        await self._pauses.put(None)

    async def step(self, seconds: float):
        await self._steps.put(seconds)

    @staticmethod
    async def wait_either[A, B](
        a: Coroutine[None, None, A], b: Coroutine[None, None, B]
    ) -> First[A] | Second[B]:
        a_task, b_task = create_task(a), create_task(b)
        dones, _waiting = await wait([a_task, b_task], return_when=FIRST_COMPLETED)
        result = dones.pop()
        if result == a_task:
            return First(a_task.result())
        elif result == b_task:
            return Second(b_task.result())
        else:
            assert_never(
                cast(Never, result)
            )  # Type checker isn't smart enough to know that result == a_task matches all Task[A]s (or same for result == b_task)
