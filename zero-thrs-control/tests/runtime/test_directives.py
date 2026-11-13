from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import ValidationError

from thrs.runtime.descriptions.simulation import Mode
from thrs.runtime.directives import DirectiveHandler, DirectiveHandling
from thrs.runtime.loop import Loop, Request
from thrs.runtime.messages import SimulationStatusMessage, SimulationStatusSetMessage

START = datetime(2026, 11, 13, 10, tzinfo=UTC)


async def test_status_set_is_requested_from_the_loop():
    channels = Mock()
    loop = AsyncMock(Loop)
    await DirectiveHandler(channels, loop).register()
    on_status_set = channels.on_status_set.call_args.args[0]

    await on_status_set(
        SimulationStatusSetMessage(
            status="stepping", pause_at=START + timedelta(minutes=10)
        )
    )

    loop.request.assert_awaited_once_with(
        Request("stepping", 1.0, START + timedelta(minutes=10))
    )


def test_status_set_rejects_a_pause_at_without_time_zone():
    with pytest.raises(ValidationError):
        SimulationStatusSetMessage.model_validate_json(
            '{"Status": "stepping", "PauseAt": "2026-11-13T10:10:00"}'
        )


async def test_status_reports_the_request():
    channels = AsyncMock()
    handling = DirectiveHandling(channels, Mode("thrs", {}, None), lambda: START)  # type: ignore[arg-type]
    loop = Loop(timedelta(seconds=1), lambda: START)
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
