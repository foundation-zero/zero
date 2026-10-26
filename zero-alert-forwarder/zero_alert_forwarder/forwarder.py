import asyncio
import logging
from collections.abc import Sequence
from datetime import timedelta
from itertools import chain, repeat

from zero_alert_forwarder.alert import Alert, AlertPriority, AlertUpdate
from zero_alert_forwarder.ntfy import Notifier
from zero_alert_forwarder.source import AlertSource

logger = logging.getLogger(__name__)


class Forwarder:
    def __init__(
        self,
        source: AlertSource,
        notifier: Notifier,
        min_priority: AlertPriority,
        updates: set[AlertUpdate],
        attempts: int,
        retry_delay: timedelta,
        reminder_delays: Sequence[timedelta] = (),
    ):
        self._source = source
        self._notifier = notifier
        self._min_rank = min_priority.rank
        self._updates = updates
        self._attempts = attempts
        self._retry_delay = retry_delay
        self._reminder_delays = reminder_delays
        self._reminders: dict[AlertKey, asyncio.Task[None]] = {}

    async def run(self) -> None:
        try:
            async for alert in self._source.alerts():
                self._silence(alert)
                if self._wanted(alert):
                    await self._forward(alert)
                    self._remind(alert)
        finally:
            for reminder in self._reminders.values():
                reminder.cancel()
            self._reminders.clear()

    def _wanted(self, alert: Alert) -> bool:
        return alert.update in self._updates and alert.priority.rank >= self._min_rank

    def _silence(self, alert: Alert) -> None:
        """Only an acknowledgement ends the reminders, also when the alarm went idle meanwhile.

        Seen for every alert, since the filters only apply to what gets forwarded.
        """
        if alert.update is AlertUpdate.ACKNOWLEDGED and (
            reminder := self._reminders.pop(_key(alert), None)
        ):
            reminder.cancel()
            logger.info(f"Stopped reminding of {alert.tag}: acknowledged")

    def _remind(self, alert: Alert) -> None:
        if not self._reminder_delays:
            return
        if previous := self._reminders.pop(_key(alert), None):
            previous.cancel()
        self._reminders[_key(alert)] = asyncio.create_task(self._ping(alert))

    async def _ping(self, alert: Alert) -> None:
        """Re-notifies at growing urgency: each delay once, the last one for ever after."""
        for delay in chain(self._reminder_delays, repeat(self._reminder_delays[-1])):
            await asyncio.sleep(delay.total_seconds())
            try:
                await self._notifier.notify(alert)
            except Exception:
                # The next reminder follows soon, so no retries of its own.
                logger.exception(f"Reminding of alert {alert.id} failed")

    async def _forward(self, alert: Alert) -> None:
        for attempt in range(1, self._attempts + 1):
            try:
                await self._notifier.notify(alert)
                logger.info(f"Forwarded alert {alert.id}: {alert.description}")
                return
            except Exception:
                logger.exception(
                    f"Forwarding alert {alert.id} failed (attempt {attempt}/{self._attempts})"
                )
                if attempt < self._attempts:
                    await asyncio.sleep(self._retry_delay.total_seconds())
        logger.error(f"Giving up on alert {alert.id}: {alert.description}")


type AlertKey = tuple[str | None, str | None, str | None]


def _key(alert: Alert) -> AlertKey:
    """The AMCS gives each update of an alarm a row of its own, so its identity is its tag."""
    return alert.system, alert.tag, alert.location
