from datetime import UTC, datetime, timedelta

import pytest

from zero_alert_forwarder.alarm_list import Alarm, AlarmList
from zero_alert_forwarder.alert import AlertPriority, AlertUpdate

from .conftest import make_alert

START = datetime(2026, 10, 22, 17, 0, tzinfo=UTC)
WINDOW = timedelta(hours=1)


def at(minutes: float) -> datetime:
    return START + timedelta(minutes=minutes)


def update(
    update: AlertUpdate,
    minutes: float = 0,
    tag: str = "PUMP-1",
    priority: AlertPriority = AlertPriority.ALARM,
    **fields,
):
    return make_alert(
        priority=priority,
        update=update,
        event_time=at(minutes),
        system="Fresh water",
        tag=tag,
        location="Engine room",
        **fields,
    )


@pytest.fixture
def alarms() -> AlarmList:
    return AlarmList(AlertPriority.WARNING, WINDOW)


def listed(alarms: AlarmList, minutes: float = 0) -> list[Alarm]:
    return alarms.message(at(minutes)).alarms


def test_activation_lists_an_active_unacknowledged_alarm(alarms: AlarmList):
    alarms.apply(update(AlertUpdate.ACTIVATED, description="Pump tripped"))

    [alarm] = listed(alarms)
    assert alarm.active
    assert not alarm.acknowledged
    assert alarm.activated_at == START
    assert alarm.last_change_at == START
    assert alarm.last_update is AlertUpdate.ACTIVATED
    assert alarm.description == "Pump tripped"
    assert (alarm.system, alarm.tag, alarm.location) == (
        "Fresh water",
        "PUMP-1",
        "Engine room",
    )


def test_acknowledgement_keeps_the_alarm_active(alarms: AlarmList):
    alarms.load([update(AlertUpdate.ACTIVATED), update(AlertUpdate.ACKNOWLEDGED, 1)])

    [alarm] = listed(alarms, 1)
    assert alarm.active
    assert alarm.acknowledged
    assert alarm.activated_at == START
    assert alarm.last_change_at == at(1)


def test_idle_ends_the_alarm_but_keeps_its_acknowledgement(alarms: AlarmList):
    alarms.load(
        [
            update(AlertUpdate.ACTIVATED),
            update(AlertUpdate.ACKNOWLEDGED, 1),
            update(AlertUpdate.IDLE, 2),
        ]
    )

    [alarm] = listed(alarms, 2)
    assert not alarm.active
    assert alarm.acknowledged
    assert alarm.activated_at == START


def test_idle_unacknowledged_alarm_stays_unacknowledged(alarms: AlarmList):
    alarms.load([update(AlertUpdate.ACTIVATED), update(AlertUpdate.IDLE, 2)])

    [alarm] = listed(alarms, 2)
    assert not alarm.active
    assert not alarm.acknowledged


def test_reactivation_needs_a_new_acknowledgement(alarms: AlarmList):
    alarms.load(
        [
            update(AlertUpdate.ACTIVATED),
            update(AlertUpdate.ACKNOWLEDGED, 1),
            update(AlertUpdate.IDLE, 2),
            update(AlertUpdate.ACTIVATED, 3),
        ]
    )

    [alarm] = listed(alarms, 3)
    assert alarm.active
    assert not alarm.acknowledged
    assert alarm.activated_at == at(3)


def test_repeated_activation_keeps_the_first_activation_time(alarms: AlarmList):
    alarms.load([update(AlertUpdate.ACTIVATED), update(AlertUpdate.ACTIVATED, 5)])

    [alarm] = listed(alarms, 5)
    assert alarm.activated_at == START
    assert alarm.last_change_at == at(5)


def test_acknowledgement_of_an_unknown_alarm_lists_it_as_ended(alarms: AlarmList):
    alarms.apply(update(AlertUpdate.ACKNOWLEDGED))

    [alarm] = listed(alarms)
    assert not alarm.active
    assert alarm.acknowledged
    assert alarm.activated_at is None


def test_idle_of_an_unknown_alarm_lists_it_as_ended(alarms: AlarmList):
    alarms.apply(update(AlertUpdate.IDLE))

    [alarm] = listed(alarms)
    assert not alarm.active
    assert alarm.activated_at is None


def test_other_updates_only_touch_known_alarms(alarms: AlarmList):
    alarms.load(
        [
            update(AlertUpdate.INHIBITED, tag="UNKNOWN"),
            update(AlertUpdate.ACTIVATED),
            update(AlertUpdate.INHIBITED, 4),
        ]
    )

    [alarm] = listed(alarms, 4)
    assert alarm.tag == "PUMP-1"
    assert alarm.active
    assert alarm.last_update is AlertUpdate.INHIBITED
    assert alarm.last_change_at == at(4)


def test_alarms_below_the_minimum_priority_are_left_out(alarms: AlarmList):
    alarms.load(
        [
            update(
                AlertUpdate.ACTIVATED, tag="CAUTION", priority=AlertPriority.CAUTION
            ),
            update(
                AlertUpdate.ACTIVATED, tag="WARNING", priority=AlertPriority.WARNING
            ),
        ]
    )

    assert [alarm.tag for alarm in listed(alarms)] == ["WARNING"]


def test_ended_alarms_stay_listed_for_the_window(alarms: AlarmList):
    alarms.load(
        [
            update(AlertUpdate.ACTIVATED, tag="ENDED"),
            update(AlertUpdate.IDLE, 10, tag="ENDED"),
            update(AlertUpdate.ACTIVATED, tag="ACTIVE"),
        ]
    )

    assert {alarm.tag for alarm in listed(alarms, 70)} == {"ENDED", "ACTIVE"}
    assert [alarm.tag for alarm in listed(alarms, 70.1)] == ["ACTIVE"]
    assert [alarm.tag for alarm in listed(alarms, 24 * 60)] == ["ACTIVE"]


def test_message_lists_newest_change_first(alarms: AlarmList):
    alarms.load(
        [
            update(AlertUpdate.ACTIVATED, 0, tag="FIRST"),
            update(AlertUpdate.ACTIVATED, 2, tag="SECOND"),
            update(AlertUpdate.ACKNOWLEDGED, 3, tag="FIRST"),
        ]
    )

    message = alarms.message(at(3))

    assert [alarm.tag for alarm in message.alarms] == ["FIRST", "SECOND"]
    assert message.recent_window_minutes == 60
    assert message.published_at == at(3)


def test_message_serializes_to_snake_case_json(alarms: AlarmList):
    alarms.apply(update(AlertUpdate.ACTIVATED))

    payload = alarms.message(START).model_dump(mode="json")

    assert payload["alarms"][0]["last_change_at"] == "2026-10-22T17:00:00Z"
    assert payload["alarms"][0]["priority"] == "Alarm"


def test_is_loaded_once_the_history_is_in(alarms: AlarmList):
    alarms.apply(update(AlertUpdate.ACTIVATED))
    assert not alarms.loaded

    alarms.load([])
    assert alarms.loaded
