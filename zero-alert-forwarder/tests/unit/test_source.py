import asyncio
from datetime import UTC, date, datetime, timedelta
from unittest.mock import Mock

import pytest

from zero_alert_forwarder.alert import Alert
from zero_alert_forwarder.liveness import Liveness
from zero_alert_forwarder.readiness import Readiness
from zero_alert_forwarder.source import PollingAlertSource

from .conftest import make_alert


class FakeTables:
    def __init__(self, days: dict[date, list[Alert]] | None = None, name: str = "db"):
        self.name = name
        self.days = days or {}
        self.failing = False
        self.hanging = False

    def raise_alert(self, day: date, alert: Alert):
        self.days.setdefault(day, []).append(alert)

    async def latest_id(self, day: date) -> int:
        await self._misbehave()
        return max((alert.id for alert in self.days.get(day, [])), default=0)

    async def read_after(self, day: date, after_id: int) -> list[Alert]:
        await self._misbehave()
        return [alert for alert in self.days.get(day, []) if alert.id > after_id]

    async def _misbehave(self):
        if self.failing:
            raise ConnectionError("database is gone")
        if self.hanging:
            await asyncio.sleep(3600)


class FakeClock:
    def __init__(self, now: datetime):
        self.now = now

    def __call__(self) -> datetime:
        return self.now


MONDAY = date(2026, 10, 19)
TUESDAY = MONDAY + timedelta(days=1)
WEDNESDAY = TUESDAY + timedelta(days=1)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(datetime(2026, 10, 19, 12, tzinfo=UTC))


def ids(alerts: list[Alert]) -> list[int]:
    return [alert.id for alert in alerts]


async def test_first_poll_skips_history(clock: FakeClock):
    tables = FakeTables({MONDAY: [make_alert(1), make_alert(2)]})
    source = PollingAlertSource([tables], timedelta(seconds=1), clock)

    assert await source.poll() == []
    tables.raise_alert(MONDAY, make_alert(3))
    assert ids(await source.poll()) == [3]


async def test_first_poll_logs_connection(
    clock: FakeClock, caplog: pytest.LogCaptureFixture
):
    source = PollingAlertSource([FakeTables()], timedelta(seconds=1), clock)

    await source.poll()

    assert "Connected to database" in caplog.text


async def test_each_alert_is_returned_once(clock: FakeClock):
    tables = FakeTables()
    source = PollingAlertSource([tables], timedelta(seconds=1), clock)
    await source.poll()

    tables.raise_alert(MONDAY, make_alert(1))
    tables.raise_alert(MONDAY, make_alert(2))
    assert ids(await source.poll()) == [1, 2]
    assert await source.poll() == []


async def test_follows_the_table_of_the_next_day(clock: FakeClock):
    tables = FakeTables({MONDAY: [make_alert(1)]})
    source = PollingAlertSource([tables], timedelta(seconds=1), clock)
    await source.poll()

    tables.raise_alert(MONDAY, make_alert(2))
    tables.raise_alert(TUESDAY, make_alert(1))
    clock.now += timedelta(days=1)

    assert ids(await source.poll()) == [2, 1]
    tables.raise_alert(TUESDAY, make_alert(2))
    assert ids(await source.poll()) == [2]


async def test_skips_days_without_a_table(clock: FakeClock):
    tables = FakeTables()
    source = PollingAlertSource([tables], timedelta(seconds=1), clock)
    await source.poll()

    tables.raise_alert(WEDNESDAY, make_alert(1))
    clock.now += timedelta(days=2)

    assert ids(await source.poll()) == [1]


async def test_waits_while_clock_is_behind_the_cursor(clock: FakeClock):
    tables = FakeTables()
    source = PollingAlertSource([tables], timedelta(seconds=1), clock)
    await source.poll()
    tables.raise_alert(MONDAY, make_alert(1))
    clock.now -= timedelta(days=1)

    assert await source.poll() == []

    clock.now += timedelta(days=1)
    assert ids(await source.poll()) == [1]


async def test_failing_poll_loses_nothing(clock: FakeClock):
    tables = FakeTables()
    source = PollingAlertSource([tables], timedelta(seconds=1), clock)
    await source.poll()
    tables.raise_alert(MONDAY, make_alert(1))

    tables.failing = True
    assert await source.poll() == []

    tables.failing = False
    assert ids(await source.poll()) == [1]


async def test_alerts_yields_polled_alerts(clock: FakeClock):
    tables = FakeTables()
    source = PollingAlertSource([tables], timedelta(0), clock)
    stream = source.alerts()
    await source.poll()

    tables.raise_alert(MONDAY, make_alert(1))
    assert (await anext(stream)).id == 1


async def test_mirrors_take_turns_without_duplicates(clock: FakeClock):
    first = FakeTables(name="first")
    second = FakeTables(name="second")
    source = PollingAlertSource([first, second], timedelta(seconds=10), clock)
    await source.poll()

    for tables in (first, second):
        tables.raise_alert(MONDAY, make_alert(1))
    assert ids(await source.poll()) == [1]
    for tables in (first, second):
        tables.raise_alert(MONDAY, make_alert(2))
    assert ids(await source.poll()) == [2]
    assert await source.poll() == []


async def test_mirror_that_lags_does_not_replay_alerts(clock: FakeClock):
    first = FakeTables(name="first")
    second = FakeTables(name="second")
    source = PollingAlertSource([first, second], timedelta(seconds=10), clock)
    await source.poll()

    first.raise_alert(MONDAY, make_alert(1))
    assert ids(await source.poll()) == []
    assert ids(await source.poll()) == [1]
    second.raise_alert(MONDAY, make_alert(1))
    assert await source.poll() == []


async def test_other_mirror_covers_for_a_failing_one(clock: FakeClock):
    first = FakeTables(name="first")
    second = FakeTables(name="second")
    source = PollingAlertSource([first, second], timedelta(seconds=10), clock)
    await source.poll()
    first.failing = True

    for tables in (first, second):
        tables.raise_alert(MONDAY, make_alert(1))
    assert ids(await source.poll()) == [1]
    assert await source.poll() == []
    for tables in (first, second):
        tables.raise_alert(MONDAY, make_alert(2))
    assert ids(await source.poll()) == [2]


async def test_logs_connection_of_each_mirror(
    clock: FakeClock, caplog: pytest.LogCaptureFixture
):
    source = PollingAlertSource(
        [FakeTables(name="first"), FakeTables(name="second")],
        timedelta(seconds=10),
        clock,
    )

    for _ in range(3):
        await source.poll()

    assert caplog.text.count("Connected to database first") == 1
    assert caplog.text.count("Connected to database second") == 1


async def test_mirrors_split_the_interval(
    clock: FakeClock, monkeypatch: pytest.MonkeyPatch
):
    class StopPolling(Exception): ...

    sleeps: list[float] = []

    async def record(seconds: float):
        sleeps.append(seconds)
        if len(sleeps) == 3:
            raise StopPolling

    monkeypatch.setattr("zero_alert_forwarder.source.asyncio.sleep", record)
    source = PollingAlertSource(
        [FakeTables(name="first"), FakeTables(name="second")],
        timedelta(seconds=10),
        clock,
    )

    with pytest.raises(StopPolling):
        [alert async for alert in source.alerts()]

    assert sleeps == [5, 5, 5]


async def test_signals_liveness_after_every_poll(
    clock: FakeClock, monkeypatch: pytest.MonkeyPatch
):
    class StopPolling(Exception): ...

    sleeps = 0

    async def stop_after_three_polls(_: float):
        nonlocal sleeps
        sleeps += 1
        if sleeps == 3:
            raise StopPolling

    monkeypatch.setattr(
        "zero_alert_forwarder.source.asyncio.sleep", stop_after_three_polls
    )
    liveness = Mock(spec=Liveness)
    tables = FakeTables()
    source = PollingAlertSource(
        [tables], timedelta(seconds=10), clock, liveness=liveness
    )
    tables.failing = True  # failing polls are signs of life too

    with pytest.raises(StopPolling):
        [alert async for alert in source.alerts()]

    assert liveness.signal.call_count == 3


async def test_lagging_mirror_does_not_lose_alerts_at_midnight(clock: FakeClock):
    first = FakeTables(name="first")
    second = FakeTables(name="second")
    clock.now = datetime(2026, 10, 19, 23, 59, 50, tzinfo=UTC)
    source = PollingAlertSource([first, second], timedelta(seconds=10), clock)
    await source.poll()
    first.raise_alert(MONDAY, make_alert(1))
    clock.now = datetime(2026, 10, 20, 0, 0, 5, tzinfo=UTC)

    assert await source.poll() == []
    assert ids(await source.poll()) == [1]


async def test_previous_day_is_retired_after_grace(clock: FakeClock):
    tables = FakeTables()
    clock.now = datetime(2026, 10, 19, 23, 59, 50, tzinfo=UTC)
    source = PollingAlertSource([tables], timedelta(seconds=10), clock)
    await source.poll()
    clock.now = datetime(2026, 10, 20, 0, 0, 5, tzinfo=UTC)
    await source.poll()

    clock.now = datetime(2026, 10, 20, 0, 1, 5, tzinfo=UTC)
    await source.poll()
    tables.raise_alert(MONDAY, make_alert(1))
    tables.raise_alert(TUESDAY, make_alert(1))

    assert ids(await source.poll()) == [1]
    assert await source.poll() == []


async def test_stalled_mirror_does_not_block_the_other(clock: FakeClock):
    first = FakeTables(name="first")
    second = FakeTables(name="second")
    source = PollingAlertSource(
        [first, second],
        timedelta(seconds=10),
        clock,
        poll_timeout=timedelta(milliseconds=50),
    )
    await source.poll()
    second.hanging = True
    for tables in (first, second):
        tables.raise_alert(MONDAY, make_alert(1))

    assert await source.poll() == []
    assert ids(await source.poll()) == [1]


async def test_signals_readiness_once_polling_is_initialised(clock: FakeClock):
    readiness = Mock(spec=Readiness)
    tables = FakeTables()
    source = PollingAlertSource(
        [tables], timedelta(seconds=1), clock, readiness=readiness
    )

    tables.failing = True
    await source.poll()
    readiness.signal.assert_not_called()

    tables.failing = False
    await source.poll()
    await source.poll()
    readiness.signal.assert_called_once()


async def test_signals_liveness_between_forwarded_alerts(
    clock: FakeClock, monkeypatch: pytest.MonkeyPatch
):
    class StopPolling(Exception): ...

    async def stop(_: float):
        raise StopPolling

    monkeypatch.setattr("zero_alert_forwarder.source.asyncio.sleep", stop)
    liveness = Mock(spec=Liveness)
    tables = FakeTables()
    source = PollingAlertSource(
        [tables], timedelta(seconds=10), clock, liveness=liveness
    )
    await source.poll()
    tables.raise_alert(MONDAY, make_alert(1))
    tables.raise_alert(MONDAY, make_alert(2))

    with pytest.raises(StopPolling):
        [alert async for alert in source.alerts()]

    assert liveness.signal.call_count == 3
