import asyncio
import logging
from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from faststream.mqtt import MQTTBroker, QoS

from zero_alert_forwarder.alarm_list import AlarmList, AlarmListMessage

logger = logging.getLogger(__name__)

ALARM_LIST_TOPIC = "alerts/alarm-list"


class Publisher(Protocol):
    def publish(self, message: AlarmListMessage) -> Awaitable[Any]: ...


def alarm_list_publisher(broker: MQTTBroker) -> Publisher:
    """Registers the alarm list on `broker`, which is also what its AsyncAPI spec is built from."""
    return broker.publisher(
        ALARM_LIST_TOPIC,
        schema=AlarmListMessage,
        qos=QoS.AT_LEAST_ONCE,
        description="The AMCS alarms that are active or changed within the recent window",
    )


class AlarmListPublisher:
    """Publishes the alarm list at a fixed interval, changed or not, as readers let it expire."""

    def __init__(
        self,
        alarms: AlarmList,
        connection: Callable[[], AbstractAsyncContextManager[Any]],
        publisher: Publisher,
        interval: timedelta,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ):
        self._alarms = alarms
        self._connection = connection
        self._publisher = publisher
        self._interval = interval
        self._now = now

    async def run(self) -> None:
        # The alarm list must not take the ntfy forwarding down with it, so nothing here raises.
        while True:
            try:
                async with self._connection():
                    logger.info(f"Publishing the alarm list to {ALARM_LIST_TOPIC}")
                    while True:
                        if self._alarms.loaded:
                            await self._publish_logged()
                        await asyncio.sleep(self._interval.total_seconds())
            except Exception:
                logger.exception("Connecting to the MQTT broker failed, retrying")
            await asyncio.sleep(self._interval.total_seconds())

    async def publish(self) -> None:
        await self._publisher.publish(self._alarms.message(self._now()))

    async def _publish_logged(self) -> None:
        """The broker client reconnects by itself, so a failed publish only waits for the next."""
        try:
            await self.publish()
        except Exception:
            logger.exception("Publishing the alarm list failed, retrying")
