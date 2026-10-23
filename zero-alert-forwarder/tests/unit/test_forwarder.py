import asyncio
from collections.abc import AsyncIterator
from datetime import timedelta

from zero_alert_forwarder.alert import Alert, AlertPriority, AlertUpdate
from zero_alert_forwarder.forwarder import Forwarder

from .conftest import make_alert


class ListSource:
    def __init__(self, *alerts: Alert):
        self._alerts = alerts

    async def alerts(self) -> AsyncIterator[Alert]:
        for alert in self._alerts:
            yield alert


class RecordingNotifier:
    def __init__(self, failures: int = 0):
        self.notified: list[int] = []
        self.calls = 0
        self._failures = failures

    async def notify(self, alert: Alert) -> None:
        self.calls += 1
        if self.calls <= self._failures:
            raise ConnectionError("ntfy unreachable")
        self.notified.append(alert.id)


async def forward(
    notifier: RecordingNotifier,
    *alerts: Alert,
    min_priority: AlertPriority = AlertPriority.WARNING,
    attempts: int = 3,
):
    await Forwarder(
        ListSource(*alerts),
        notifier,
        min_priority,
        {AlertUpdate.ACTIVATED},
        attempts,
        timedelta(0),
    ).run()


async def test_forwards_activated_alerts():
    notifier = RecordingNotifier()

    await forward(notifier, make_alert(1), make_alert(2))

    assert notifier.notified == [1, 2]


async def test_ignores_other_updates():
    notifier = RecordingNotifier()

    await forward(
        notifier,
        make_alert(1, update=AlertUpdate.IDLE),
        make_alert(2, update=AlertUpdate.ACKNOWLEDGED),
        make_alert(3),
    )

    assert notifier.notified == [3]


async def test_ignores_alerts_below_minimum_priority():
    notifier = RecordingNotifier()

    await forward(
        notifier,
        make_alert(1, AlertPriority.CAUTION),
        make_alert(2, AlertPriority.WARNING),
        make_alert(3, AlertPriority.EMERGENCY),
        make_alert(4, AlertPriority.EVENT),
    )

    assert notifier.notified == [2, 3]


async def test_minimum_priority_can_be_lowered():
    notifier = RecordingNotifier()

    await forward(
        notifier,
        make_alert(1, AlertPriority.CAUTION),
        min_priority=AlertPriority.CAUTION,
    )

    assert notifier.notified == [1]


async def test_minimum_priority_distinguishes_the_top_levels():
    notifier = RecordingNotifier()
    alerts = [
        make_alert(1, AlertPriority.ALARM),
        make_alert(2, AlertPriority.EMERGENCY),
        make_alert(3, AlertPriority.GEA),
    ]

    await forward(notifier, *alerts, min_priority=AlertPriority.EMERGENCY)
    assert notifier.notified == [2, 3]

    notifier.notified.clear()
    await forward(notifier, *alerts, min_priority=AlertPriority.GEA)
    assert notifier.notified == [3]


async def test_unknown_priority_is_forwarded_by_default():
    notifier = RecordingNotifier()

    await forward(notifier, make_alert(1, AlertPriority.UNKNOWN))

    assert notifier.notified == [1]


async def test_retries_failed_notification():
    notifier = RecordingNotifier(failures=2)

    await forward(notifier, make_alert(1))

    assert notifier.notified == [1]
    assert notifier.calls == 3


async def test_gives_up_but_continues_with_next_alert():
    notifier = RecordingNotifier(failures=3)

    await forward(notifier, make_alert(1), make_alert(2))

    assert notifier.notified == [2]
    assert notifier.calls == 4


class PacedSource:
    """Yields each alert after a pause, during which reminders can fire."""

    def __init__(self, *steps: tuple[float, Alert]):
        self._steps = steps

    async def alerts(self) -> AsyncIterator[Alert]:
        for pause, alert in self._steps:
            await asyncio.sleep(pause)
            yield alert
        await asyncio.sleep(0.1)


async def remind(notifier: RecordingNotifier, *steps: tuple[float, Alert]):
    await Forwarder(
        PacedSource(*steps),
        notifier,
        AlertPriority.WARNING,
        {AlertUpdate.ACTIVATED},
        1,
        timedelta(0),
        [timedelta(seconds=0.02), timedelta(seconds=0.01)],
    ).run()


async def test_reminds_until_silenced():
    notifier = RecordingNotifier()

    await remind(
        notifier,
        (0, make_alert(1, tag="pump")),
        (0.2, make_alert(2, update=AlertUpdate.ACKNOWLEDGED, tag="pump")),
    )

    reminded = len(notifier.notified)
    assert reminded > 3
    assert set(notifier.notified) == {1}


async def test_stops_reminding_once_acknowledged():
    notifier = RecordingNotifier()

    await remind(
        notifier,
        (0, make_alert(1, tag="pump")),
        (0.05, make_alert(2, update=AlertUpdate.ACKNOWLEDGED, tag="pump")),
    )

    # The final pause is long enough for several more reminders, had any survived.
    assert len(notifier.notified) < 6


async def test_acknowledging_another_alarm_does_not_silence():
    notifier = RecordingNotifier()

    await remind(
        notifier,
        (0, make_alert(1, tag="pump")),
        (0.05, make_alert(2, update=AlertUpdate.ACKNOWLEDGED, tag="fan")),
    )

    assert len(notifier.notified) > 6


async def test_does_not_remind_without_delays():
    notifier = RecordingNotifier()

    await Forwarder(
        PacedSource((0, make_alert(1))),
        notifier,
        AlertPriority.WARNING,
        {AlertUpdate.ACTIVATED},
        1,
        timedelta(0),
    ).run()

    assert notifier.notified == [1]


async def test_keeps_reminding_when_alarm_goes_idle_unacknowledged():
    notifier = RecordingNotifier()

    await remind(
        notifier,
        (0, make_alert(1, tag="pump")),
        (0.05, make_alert(2, update=AlertUpdate.IDLE, tag="pump")),
    )

    assert len(notifier.notified) > 6
