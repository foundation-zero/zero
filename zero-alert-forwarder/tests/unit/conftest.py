from datetime import UTC, datetime

from zero_alert_forwarder.alert import Alert, AlertPriority, AlertUpdate


def make_alert(
    id: int = 1,
    priority: AlertPriority = AlertPriority.ALARM,
    update: AlertUpdate = AlertUpdate.ACTIVATED,
    **fields,
) -> Alert:
    return Alert(
        id=id,
        event_time=fields.pop("event_time", datetime(2026, 10, 22, 17, 0, tzinfo=UTC)),
        priority=priority,
        update=update,
        **fields,
    )
