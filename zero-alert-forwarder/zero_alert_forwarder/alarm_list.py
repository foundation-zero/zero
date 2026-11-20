from collections.abc import Iterable
from datetime import datetime, timedelta

from pydantic import BaseModel

from zero_alert_forwarder.alert import Alert, AlertPriority, AlertUpdate


class Alarm(BaseModel):
    """The state of one AMCS alarm, folded from the rows of its updates."""

    system: str | None
    tag: str | None
    location: str | None
    description: str | None
    priority: AlertPriority
    active: bool
    acknowledged: bool
    # Unknown when the activation happened before the rows that were read.
    activated_at: datetime | None
    last_change_at: datetime
    last_update: AlertUpdate


class AlarmListMessage(BaseModel):
    """The alarms that are active or changed within the recent window, newest change first."""

    alarms: list[Alarm]
    recent_window_minutes: float
    published_at: datetime


type AlarmKey = tuple[str | None, str | None, str | None]


def alarm_key(alert: Alert) -> AlarmKey:
    """Every row of an alarm carries its system, tag and location, which together identify it."""
    return alert.system, alert.tag, alert.location


class AlarmList:
    """Every alarm that is active, or that changed within the recent window."""

    def __init__(self, min_priority: AlertPriority, recent_window: timedelta):
        self._min_rank = min_priority.rank
        self._recent_window = recent_window
        self._alarms: dict[AlarmKey, Alarm] = {}

    def apply_all(self, alerts: Iterable[Alert]) -> None:
        for alert in alerts:
            self.apply(alert)

    def apply(self, alert: Alert) -> None:
        if alert.priority.rank < self._min_rank:
            return
        key = alarm_key(alert)
        previous = self._alarms.get(key)
        match alert.update:
            case AlertUpdate.ACTIVATED:
                self._alarms[key] = _changed(
                    alert,
                    active=True,
                    acknowledged=False,
                    activated_at=previous.activated_at
                    if previous and previous.active
                    else alert.event_time,
                )
            case AlertUpdate.ACKNOWLEDGED:
                # Without the activation, it may as well have ended already; showing it as
                # active could leave it listed for good, as no Idle may follow.
                self._alarms[key] = _changed(
                    alert,
                    active=previous.active if previous else False,
                    acknowledged=True,
                    activated_at=previous.activated_at if previous else None,
                )
            case AlertUpdate.IDLE:
                self._alarms[key] = _changed(
                    alert,
                    active=False,
                    acknowledged=previous.acknowledged if previous else False,
                    activated_at=previous.activated_at if previous else None,
                )
            case _ if previous:
                self._alarms[key] = previous.model_copy(
                    update={
                        "last_change_at": alert.event_time,
                        "last_update": alert.update,
                    }
                )
            case _:
                pass

    def message(self, now: datetime) -> AlarmListMessage:
        """Drops the alarms that ended before the recent window, then lists the rest."""
        since = now - self._recent_window
        self._alarms = {
            key: alarm
            for key, alarm in self._alarms.items()
            if alarm.active or alarm.last_change_at >= since
        }
        return AlarmListMessage(
            alarms=sorted(
                self._alarms.values(),
                key=lambda alarm: alarm.last_change_at,
                reverse=True,
            ),
            recent_window_minutes=self._recent_window.total_seconds() / 60,
            published_at=now,
        )


def _changed(
    alert: Alert, active: bool, acknowledged: bool, activated_at: datetime | None
) -> Alarm:
    return Alarm(
        system=alert.system,
        tag=alert.tag,
        location=alert.location,
        description=alert.description,
        priority=alert.priority,
        active=active,
        acknowledged=acknowledged,
        activated_at=activated_at,
        last_change_at=alert.event_time,
        last_update=alert.update,
    )
