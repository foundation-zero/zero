import asyncio
import logging
from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager
from datetime import UTC, datetime, timedelta
from typing import Protocol

import aiomqtt

from zero_alert_forwarder.alarm_list import AlarmList

logger = logging.getLogger(__name__)

ALARM_LIST_TOPIC = "alerts/alarm-list"


class MqttClient(Protocol):
    def publish(self, topic: str, payload: str, qos: int) -> Awaitable[None]: ...


class AlarmListPublisher:
    """Publishes the alarm list at a fixed interval, changed or not, as readers let it expire."""

    def __init__(
        self,
        alarms: AlarmList,
        connect: Callable[[], AbstractAsyncContextManager[MqttClient]],
        interval: timedelta,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ):
        self._alarms = alarms
        self._connect = connect
        self._interval = interval
        self._now = now

    async def run(self) -> None:
        while True:
            try:
                async with self._connect() as client:
                    logger.info(f"Publishing the alarm list to {ALARM_LIST_TOPIC}")
                    while True:
                        await self.publish(client)
                        await asyncio.sleep(self._interval.total_seconds())
            except aiomqtt.MqttError as error:
                logger.warning(f"Lost the MQTT broker ({error}), reconnecting")
            except Exception:
                # The alarm list must not take the ntfy forwarding down with it.
                logger.exception("Publishing the alarm list failed, retrying")
            await asyncio.sleep(self._interval.total_seconds())

    async def publish(self, client: MqttClient) -> None:
        message = self._alarms.message(self._now())
        await client.publish(ALARM_LIST_TOPIC, message.model_dump_json(), qos=1)
