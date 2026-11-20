import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock, call

import pytest
from pydantic import ValidationError

from thrs.runtime.descriptions.simulation import Mode
from thrs.runtime.directives import DirectiveHandling
from thrs.runtime.loop import ControllableLoop, Request
from thrs.runtime.messages import SimulationStatusMessage, SimulationStatusSetMessage

START = datetime(2026, 11, 13, 10, tzinfo=UTC)


def test_status_set_is_requested_from_the_loop():
    channels = Mock()
    loop = Mock(ControllableLoop)

    DirectiveHandling(channels, Mock(Mode), lambda: datetime.fromtimestamp(0)).register(
        loop
    )
    on_status_set = channels.on_status_set.call_args.args[0]

    on_status_set(
        SimulationStatusSetMessage(
            status="stepping", pause_at=START + timedelta(minutes=10)
        )
    )

    assert loop.request.call_args_list == [
        call(Request("stepping", 1.0, START + timedelta(minutes=10)))
    ]


async def test_a_status_set_before_the_loop_runs_is_kept():
    channels = Mock(send_simulation_status=AsyncMock())
    handling = DirectiveHandling(channels, Mode("thrs", {}, None), lambda: START)
    loop = ControllableLoop(timedelta(seconds=1), lambda: START, handling)
    on_status_set = channels.on_status_set.call_args.args[0]
    ticked = asyncio.Event()
    runner = Mock(tick=AsyncMock(side_effect=ticked.set))

    # A retained directive can arrive as soon as the connector subscribes.
    on_status_set(SimulationStatusSetMessage(status="running"))
    loop_task = asyncio.create_task(loop.loop(runner))
    try:
        await asyncio.wait_for(ticked.wait(), timeout=1)
    finally:
        loop_task.cancel()

    assert loop.requested == Request("running", 1.0, None)


def test_status_set_rejects_a_pause_at_without_time_zone():
    with pytest.raises(ValidationError):
        SimulationStatusSetMessage.model_validate_json(
            '{"Status": "stepping", "PauseAt": "2026-11-13T10:10:00"}'
        )


async def test_clear_previous_clears_the_status():
    channels = AsyncMock()
    handling = DirectiveHandling(channels, Mode("thrs", {}, None), lambda: START)

    await handling.clear_previous()

    assert channels.send_simulation_status.await_args_list == [call(None)]


async def test_status_reports_the_request():
    channels = AsyncMock()
    handling = DirectiveHandling(channels, Mode("thrs", {}, None), lambda: START)
    loop = ControllableLoop(timedelta(seconds=1), lambda: START)
    loop.requested = Request("running", 2.0, START + timedelta(hours=1))

    await handling.send_status(loop, "running")

    channels.send_simulation_status.assert_awaited_once_with(
        SimulationStatusMessage(
            mode="thrs",
            status="running",
            control_modules=[],
            simulation_time=START,
            playback_rate=2.0,
            pause_at=START + timedelta(hours=1),
        )
    )
