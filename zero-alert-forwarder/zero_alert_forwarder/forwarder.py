import asyncio
import logging
from datetime import timedelta

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
    ):
        self._source = source
        self._notifier = notifier
        self._min_rank = min_priority.rank
        self._updates = updates
        self._attempts = attempts
        self._retry_delay = retry_delay

    async def run(self) -> None:
        async for alert in self._source.alerts():
            if self._wanted(alert):
                await self._forward(alert)

    def _wanted(self, alert: Alert) -> bool:
        return alert.update in self._updates and alert.priority.rank >= self._min_rank

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
