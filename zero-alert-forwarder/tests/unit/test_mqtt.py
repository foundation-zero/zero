import asyncio
import json
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

import aiomqtt
import pytest

from zero_alert_forwarder.alarm_list import AlarmList
from zero_alert_forwarder.alert import AlertPriority
from zero_alert_forwarder.mqtt import ALARM_LIST_TOPIC, AlarmListPublisher

from .conftest import make_alert

NOW = datetime(2026, 10, 22, 17, 30, tzinfo=UTC)


class RecordingClient:
    def __init__(self):
        self.published: list[tuple[str, dict, int]] = []

    async def publish(self, topic: str, payload: str, qos: int) -> None:
        self.published.append((topic, json.loads(payload), qos))


def make_alarms() -> AlarmList:
    alarms = AlarmList(AlertPriority.WARNING, timedelta(hours=1))
    alarms.apply(make_alert(tag="PUMP-1"))
    return alarms


async def test_publishes_the_alarm_list():
    client = RecordingClient()
    publisher = AlarmListPublisher(
        make_alarms(), lambda: _connected(client), timedelta(seconds=5), now=lambda: NOW
    )

    await publisher.publish(client)

    [(topic, payload, qos)] = client.published
    assert topic == ALARM_LIST_TOPIC
    assert qos == 1
    assert [alarm["tag"] for alarm in payload["alarms"]] == ["PUMP-1"]
    assert payload["published_at"] == "2026-10-22T17:30:00Z"


async def test_keeps_publishing_at_the_interval():
    client = RecordingClient()
    publisher = AlarmListPublisher(
        make_alarms(), lambda: _connected(client), timedelta(seconds=0.01)
    )

    with pytest.raises(TimeoutError):
        async with asyncio.timeout(0.1):
            await publisher.run()

    assert len(client.published) > 2


async def test_reconnects_after_losing_the_broker(caplog: pytest.LogCaptureFixture):
    client = RecordingClient()
    connections = 0

    @asynccontextmanager
    async def flaky():
        nonlocal connections
        connections += 1
        if connections == 1:
            raise aiomqtt.MqttError("broker is gone")
        yield client

    publisher = AlarmListPublisher(make_alarms(), flaky, timedelta(seconds=0.01))

    with pytest.raises(TimeoutError):
        async with asyncio.timeout(0.1):
            await publisher.run()

    assert connections == 2
    assert client.published
    assert "Lost the MQTT broker" in caplog.text


async def test_keeps_publishing_after_an_unexpected_error(
    caplog: pytest.LogCaptureFixture,
):
    client = RecordingClient()
    publishes = 0
    original = client.publish

    async def failing_once(topic: str, payload: str, qos: int) -> None:
        nonlocal publishes
        publishes += 1
        if publishes == 1:
            raise ValueError("unexpected")
        await original(topic, payload, qos)

    client.publish = failing_once
    publisher = AlarmListPublisher(
        make_alarms(), lambda: _connected(client), timedelta(seconds=0.01)
    )

    with pytest.raises(TimeoutError):
        async with asyncio.timeout(0.1):
            await publisher.run()

    assert client.published
    assert "Publishing the alarm list failed" in caplog.text


@asynccontextmanager
async def _connected(client: RecordingClient):
    yield client
