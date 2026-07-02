from __future__ import annotations

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from thrs.runtime.loop import Loop, LoopHooks


def make_runner(block_after_first_call: bool = False):
    started = asyncio.Event()
    release = asyncio.Event()
    calls: list[int] = []

    async def run(n_ticks: int) -> None:
        calls.append(n_ticks)
        started.set()

        if block_after_first_call:
            await release.wait()

    runner = MagicMock()
    runner.run = AsyncMock(side_effect=run)
    runner.calls = calls
    runner.started = started
    runner.release = release
    return runner


def make_hooks(hook_calls: list[str]) -> LoopHooks:
    async def available_hook(_: Loop) -> None:
        hook_calls.append("available")

    async def running_hook(_: Loop) -> None:
        hook_calls.append("running")

    async def stepping_hook(_: Loop) -> None:
        hook_calls.append("stepping")

    return LoopHooks(available_hook, running_hook, stepping_hook)


@pytest.mark.asyncio
async def test_loop_steps_runner_for_requested_ticks():
    loop = Loop(tick_duration=timedelta(seconds=2))
    runner = make_runner()
    hook_calls: list[str] = []
    hooks = make_hooks(hook_calls)

    loop_task = asyncio.create_task(loop.loop(runner, hooks))

    try:
        await loop.step(5)

        await asyncio.wait_for(runner.started.wait(), timeout=1)

        assert runner.calls == [2]
        runner.run.assert_awaited_once_with(2)
        assert hook_calls[:2] == ["available", "stepping"]
    finally:
        loop_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await loop_task


@pytest.mark.asyncio
async def test_loop_play_runs_until_pause():
    loop = Loop(tick_duration=timedelta(seconds=1))
    runner = make_runner(block_after_first_call=True)
    hook_calls: list[str] = []
    hooks = make_hooks(hook_calls)

    loop_task = asyncio.create_task(loop.loop(runner, hooks))

    try:
        await loop.play(2.0)

        await asyncio.wait_for(runner.started.wait(), timeout=1)
        assert runner.calls == [1]
        runner.run.assert_awaited_once_with(1)
        assert hook_calls == ["available", "running"]

        await loop.pause()
        runner.release.set()

        assert runner.calls == [1]
        assert hook_calls[:2] == ["available", "running"]
    finally:
        loop_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await loop_task
