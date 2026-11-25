import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

import pytest

from zero_alert_forwarder.alarm_list import AlarmList, AlarmListMessage
from zero_alert_forwarder.alert import AlertPriority
from zero_alert_forwarder.mqtt import AlarmListPublisher

from .conftest import make_alert

NOW = datetime(2026, 10, 22, 17, 30, tzinfo=UTC)


class RecordingPublisher:
    def __init__(self, failures: int = 0):
        self.published: list[AlarmListMessage] = []
        self._failures = failures

    async def publish(self, message: AlarmListMessage) -> None:
        if self._failures:
            self._failures -= 1
            raise ConnectionError("broker is gone")
        self.published.append(message)


def make_alarms() -> AlarmList:
    alarms = AlarmList(AlertPriority.WARNING, timedelta(hours=1))
    alarms.load([make_alert(tag="PUMP-1")])
    return alarms


@asynccontextmanager
async def connected():
    yield


async def run_briefly(publisher: AlarmListPublisher) -> None:
    with pytest.raises(TimeoutError):
        async with asyncio.timeout(0.1):
            await publisher.run()


async def test_publishes_the_alarm_list():
    publisher = RecordingPublisher()

    await AlarmListPublisher(
        make_alarms(), connected, publisher, timedelta(seconds=5), now=lambda: NOW
    ).publish()

    [message] = publisher.published
    assert [alarm.tag for alarm in message.alarms] == ["PUMP-1"]
    assert message.published_at == NOW


async def test_keeps_publishing_at_the_interval():
    publisher = RecordingPublisher()

    await run_briefly(
        AlarmListPublisher(make_alarms(), connected, publisher, timedelta(seconds=0.01))
    )

    assert len(publisher.published) > 2


async def test_keeps_publishing_after_a_failed_publish(
    caplog: pytest.LogCaptureFixture,
):
    publisher = RecordingPublisher(failures=1)

    await run_briefly(
        AlarmListPublisher(make_alarms(), connected, publisher, timedelta(seconds=0.01))
    )

    assert publisher.published
    assert "Publishing the alarm list failed" in caplog.text


async def test_retries_a_failed_connection(caplog: pytest.LogCaptureFixture):
    publisher = RecordingPublisher()
    attempts = 0

    @asynccontextmanager
    async def flaky():
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ConnectionRefusedError("broker is not up yet")
        yield

    await run_briefly(
        AlarmListPublisher(make_alarms(), flaky, publisher, timedelta(seconds=0.01))
    )

    assert attempts == 2
    assert publisher.published
    assert "Connecting to the MQTT broker failed" in caplog.text


async def test_waits_for_the_history_before_publishing():
    alarms = AlarmList(AlertPriority.WARNING, timedelta(hours=1))
    publisher = RecordingPublisher()
    alarm_list = AlarmListPublisher(
        alarms, connected, publisher, timedelta(seconds=0.01)
    )

    await run_briefly(alarm_list)
    assert publisher.published == []

    alarms.load([make_alert(tag="PUMP-1")])
    await run_briefly(alarm_list)
    assert publisher.published
