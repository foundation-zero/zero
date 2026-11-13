from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from functools import partial
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from thrs.runtime.loop import Loop, LoopHooks, Request

START = datetime(2026, 11, 13, 10, tzinfo=UTC)


class Clock:
    """A simulation clock that each tick of the runner advances."""

    def __init__(self, tick_duration: timedelta):
        self.tick_duration = tick_duration
        self.time = START

    def __call__(self) -> datetime:
        return self.time


def make_runner(clock: Clock, block_after_first_call: bool = False):
    started = asyncio.Event()
    release = asyncio.Event()
    calls = Mock()

    async def tick() -> None:
        calls()
        clock.time += clock.tick_duration
        started.set()

        if block_after_first_call:
            await release.wait()

    runner = MagicMock()
    runner.tick = AsyncMock(side_effect=tick)
    runner.calls = calls
    runner.started = started
    runner.release = release
    return runner


class RecordingHooks:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self._recorded = asyncio.Condition()

    def hooks(self) -> LoopHooks:
        return LoopHooks(
            partial(self._record, "available"),
            partial(self._record, "running"),
            partial(self._record, "stepping"),
        )

    async def _record(self, name: str, _loop: Loop) -> None:
        self.calls.append(name)
        async with self._recorded:
            self._recorded.notify_all()

    async def wait_until(self, predicate: Callable[[list[str]], bool]) -> None:
        async with self._recorded:
            await asyncio.wait_for(
                self._recorded.wait_for(lambda: predicate(self.calls)), timeout=1
            )

    async def wait_until_available(self, times: int) -> None:
        await self.wait_until(lambda calls: calls.count("available") >= times)


@asynccontextmanager
async def looping(loop: Loop, runner, hooks: RecordingHooks) -> AsyncIterator[None]:
    loop_task = asyncio.create_task(loop.loop(runner, hooks.hooks()))
    try:
        yield
    finally:
        loop_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await loop_task


async def test_loop_steps_to_pause_at():
    clock = Clock(timedelta(seconds=2))
    loop = Loop(clock.tick_duration, clock)
    runner = make_runner(clock)
    hooks = RecordingHooks()

    async with looping(loop, runner, hooks):
        await loop.request(Request("stepping", 1.0, START + timedelta(seconds=5)))
        await hooks.wait_until_available(2)

    # The first tick at or after pause_at: 2 s, 4 s, 6 s.
    assert runner.calls.call_count == 3
    assert clock.time == START + timedelta(seconds=6)
    assert hooks.calls == ["available", "stepping", "available"]


async def test_loop_stepping_without_a_later_pause_at_does_nothing():
    clock = Clock(timedelta(seconds=1))
    loop = Loop(clock.tick_duration, clock)
    runner = make_runner(clock)
    hooks = RecordingHooks()

    async with looping(loop, runner, hooks):
        await loop.request(Request("stepping", 1.0, START))
        await hooks.wait_until_available(2)

    assert runner.calls.call_count == 0
    assert hooks.calls == ["available", "available"]


async def test_loop_runs_until_pause_at():
    clock = Clock(timedelta(milliseconds=100))
    loop = Loop(clock.tick_duration, clock)
    runner = make_runner(clock)
    hooks = RecordingHooks()

    async with looping(loop, runner, hooks):
        await loop.request(Request("running", 10, START + timedelta(milliseconds=300)))
        await hooks.wait_until_available(2)

    assert runner.calls.call_count == 3
    assert hooks.calls == [
        "available",
        "running",
        "running",
        "running",
        "running",
        "available",
    ]


async def test_loop_runs_on_with_a_past_pause_at():
    clock = Clock(timedelta(milliseconds=100))
    loop = Loop(clock.tick_duration, clock)
    runner = make_runner(clock)
    hooks = RecordingHooks()

    async with looping(loop, runner, hooks):
        await loop.request(Request("running", 10, START))
        await hooks.wait_until(lambda calls: calls.count("running") > 3)
        await loop.pause()
        await hooks.wait_until_available(2)

    assert runner.calls.call_count >= 3


async def test_loop_pause_interrupts_stepping():
    clock = Clock(timedelta(seconds=1))
    loop = Loop(clock.tick_duration, clock)
    runner = make_runner(clock, block_after_first_call=True)
    hooks = RecordingHooks()

    async with looping(loop, runner, hooks):
        await loop.request(Request("stepping", 1.0, START + timedelta(hours=1)))
        await asyncio.wait_for(runner.started.wait(), timeout=1)

        await loop.pause()
        runner.release.set()
        await hooks.wait_until_available(2)

    assert runner.calls.call_count == 1
    assert hooks.calls[:3] == ["available", "stepping", "available"]


async def test_loop_keeps_the_last_request():
    clock = Clock(timedelta(seconds=1))
    loop = Loop(clock.tick_duration, clock)
    runner = make_runner(clock, block_after_first_call=True)
    hooks = RecordingHooks()
    request = Request("running", 2.0, START + timedelta(minutes=1))

    async with looping(loop, runner, hooks):
        await loop.request(request)
        await asyncio.wait_for(runner.started.wait(), timeout=1)

        assert loop.requested == request


async def test_loop_play_runs_until_pause():
    clock = Clock(timedelta(seconds=1))
    loop = Loop(clock.tick_duration, clock)
    runner = make_runner(clock, block_after_first_call=True)
    hooks = RecordingHooks()

    async with looping(loop, runner, hooks):
        await loop.play(2.0)

        await asyncio.wait_for(runner.started.wait(), timeout=1)
        assert runner.calls.call_count == 1
        assert hooks.calls == ["available", "running"]

        await loop.pause()
        runner.release.set()
        await hooks.wait_until_available(2)

    assert runner.calls.call_count == 1
    assert hooks.calls[:4] == ["available", "running", "running", "available"]
