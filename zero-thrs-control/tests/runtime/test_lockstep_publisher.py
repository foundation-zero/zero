import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from thrs.runtime.loop import Loop, LoopHooks
from thrs.runtime.runners.lockstep import LockstepPublisher

INTERVAL = timedelta(milliseconds=10)


def make_publisher(events: list[str], publish: AsyncMock | None = None):
    async def record(event: str) -> None:
        events.append(event)

    runner = MagicMock()
    runner.publish = publish or AsyncMock(side_effect=lambda: events.append("publish"))

    status_hooks = LoopHooks(
        available=lambda _: record("available"),
        running=lambda _: record("running"),
        stepping=lambda _: record("stepping"),
    )
    return LockstepPublisher(runner, status_hooks, INTERVAL)


async def test_publishes_with_running_status_at_interval_while_playing():
    events: list[str] = []
    hooks = make_publisher(events).hooks()
    loop = Loop(tick_duration=timedelta(seconds=1))

    await hooks.running(loop)
    await asyncio.sleep(INTERVAL.total_seconds() * 5)
    await hooks.available(loop)

    assert events[0] == "running"
    assert events[1:4] == ["publish", "running", "publish"]
    assert events[-2:] == ["publish", "available"]


async def test_stops_publishing_once_available():
    events: list[str] = []
    hooks = make_publisher(events).hooks()
    loop = Loop(tick_duration=timedelta(seconds=1))

    await hooks.running(loop)
    await hooks.available(loop)
    events_when_available = list(events)
    await asyncio.sleep(INTERVAL.total_seconds() * 5)

    assert events == events_when_available == ["running", "publish", "available"]


async def test_publishes_after_a_step():
    events: list[str] = []
    hooks = make_publisher(events).hooks()
    loop = Loop(tick_duration=timedelta(seconds=1))

    await hooks.stepping(loop)
    await hooks.available(loop)

    assert events == ["stepping", "publish", "available"]


async def test_periodic_publish_failure_surfaces_when_available():
    events: list[str] = []
    publish = AsyncMock(side_effect=ConnectionError("broker gone"))
    hooks = make_publisher(events, publish).hooks()
    loop = Loop(tick_duration=timedelta(seconds=1))

    await hooks.running(loop)
    await asyncio.sleep(INTERVAL.total_seconds() * 3)

    with pytest.raises(ConnectionError, match="broker gone"):
        await hooks.available(loop)
