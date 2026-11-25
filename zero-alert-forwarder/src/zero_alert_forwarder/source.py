import asyncio
import logging
from collections.abc import AsyncIterator, Callable, Iterable, Sequence
from datetime import UTC, date, datetime, time, timedelta
from typing import Protocol

from zero_alert_forwarder.alert import Alert
from zero_alert_forwarder.liveness import Liveness
from zero_alert_forwarder.readiness import Readiness

logger = logging.getLogger(__name__)

# How long a day stays polled after it ended, for mirrors that lag behind on its last alerts.
ROLLOVER_GRACE = timedelta(minutes=1)


class AlertSource(Protocol):
    def alerts(self) -> AsyncIterator[Alert]:
        """Yields each alert exactly once, in the order it was raised."""
        ...


class DayTables(Protocol):
    """Read-only access to the AMCS alerts, which are sharded into a table per UTC day."""

    name: str

    async def latest_id(self, day: date) -> int:
        """Highest alert id of the day, or 0 when it has no alerts or no table yet."""
        ...

    async def read_after(self, day: date, after_id: int) -> list[Alert]:
        """Alerts of the day with an id above ``after_id``, oldest first."""
        ...


class History(Protocol):
    def load(self, alerts: Iterable[Alert]) -> None:
        """Takes the alerts raised before polling started, oldest first."""
        ...


class PollingAlertSource:
    """Polls the day tables, since the AMCS database offers no way to be notified.

    Several tables are mirrors of each other and take turns, offset by an equal share
    of the interval. Ids are the same on every mirror, so they share one cursor per day.
    """

    def __init__(
        self,
        tables: Sequence[DayTables],
        interval: timedelta,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
        liveness: Liveness = Liveness(None),
        readiness: Readiness = Readiness(None),
        poll_timeout: timedelta = timedelta(seconds=10),
        history: History | None = None,
        history_window: timedelta = timedelta(0),
        history_timeout: timedelta = timedelta(seconds=60),
    ):
        self._tables = tables
        self._interval = interval
        self._now = now
        self._liveness = liveness
        self._readiness = readiness
        self._poll_timeout = poll_timeout
        self._history = history
        self._history_window = history_window
        self._history_timeout = history_timeout
        self._turn = 0
        self._connected: set[str] = set()
        self._last_ids: dict[date, int] | None = None

    async def alerts(self) -> AsyncIterator[Alert]:
        while True:
            new_alerts = await self.poll()
            self._liveness.signal()
            for alert in new_alerts:
                yield alert
                # Forwarding blocks here, a large batch would otherwise look like a hung loop.
                self._liveness.signal()
            await asyncio.sleep(self._interval.total_seconds() / len(self._tables))

    async def poll(self) -> list[Alert]:
        """Returns the alerts raised since the previous poll.

        The cursor only moves once the whole poll succeeded, so a failing poll is
        retried by the next one without losing anything.
        """
        tables = self._tables[self._turn % len(self._tables)]
        self._turn += 1
        try:
            # A stalled mirror must not keep the other one from taking its turn.
            async with asyncio.timeout(self._timeout().total_seconds()):
                new_alerts = await self._poll(tables)
        except Exception:
            logger.exception(
                f"Polling alerts of {tables.name} failed, retrying next turn"
            )
            return []
        if tables.name not in self._connected:
            self._connected.add(tables.name)
            logger.info(f"Connected to database {tables.name}")
        return new_alerts

    def _timeout(self) -> timedelta:
        """A whole day of history takes longer to read than the alerts since the last poll."""
        reads_history = self._history is not None and self._last_ids is None
        return self._history_timeout if reads_history else self._poll_timeout

    async def _poll(self, tables: DayTables) -> list[Alert]:
        now = self._now()
        today = now.date()
        if self._last_ids is None:
            # History is not returned, otherwise every restart would notify of the day's alerts.
            self._last_ids = (
                await self._read_history(tables, now, self._history)
                if self._history
                else {today: await tables.latest_id(today)}
            )
            logger.info(
                f"Forwarding alerts after id {self._last_ids[today]} of {today}"
            )
            self._readiness.signal()
            return []

        first = min(self._last_ids)
        if today < max(self._last_ids):
            # Clocks can be off after a power loss; wait for them to catch up.
            return []

        days = [
            first + timedelta(days=offset) for offset in range((today - first).days + 1)
        ]
        reads = [
            await tables.read_after(day, self._last_ids.get(day, 0)) for day in days
        ]
        last_ids = {
            day: max([self._last_ids.get(day, 0), *(alert.id for alert in read)])
            for day, read in zip(days, reads, strict=True)
        }
        self._last_ids = {
            day: last_id
            for day, last_id in last_ids.items()
            if day == today or now < _end_of(day) + ROLLOVER_GRACE
        }
        return [alert for read in reads for alert in read]

    async def _read_history(
        self, tables: DayTables, now: datetime, history: History
    ) -> dict[date, int]:
        """Hands the whole of today to the history, and the days the window reaches into.

        All of today rather than only the window, to also learn of alarms that were raised
        earlier and are still active.
        """
        today = now.date()
        first = min(today, (now - self._history_window).date())
        days = [
            first + timedelta(days=offset) for offset in range((today - first).days + 1)
        ]
        reads = [await tables.read_after(day, 0) for day in days]
        history.load(alert for read in reads for alert in read)
        logger.info(
            f"Read {sum(len(read) for read in reads)} alerts of {', '.join(str(day) for day in days)}"
            " as history"
        )
        return {
            day: max((alert.id for alert in read), default=0)
            for day, read in zip(days, reads, strict=True)
        }


def _end_of(day: date) -> datetime:
    return datetime.combine(day + timedelta(days=1), time.min, UTC)
