import pytest

from zero_alert_forwarder.alert import AlertPriority, AlertUpdate

from .conftest import make_alert


@pytest.mark.parametrize(
    "priority, severity",
    [
        ("GEA", 5),
        ("Emergency", 5),
        ("Alarm", 5),
        ("Warning", 4),
        ("Caution", 3),
        ("Event", 1),
        ("SomethingNew", 4),
    ],
)
def test_severity(priority: str, severity: int):
    assert AlertPriority(priority).severity == severity


def test_unknown_values_do_not_fail_validation():
    alert = make_alert(priority="SomethingNew", update="Rebooted")  # type: ignore[arg-type]
    assert alert.priority is AlertPriority.UNKNOWN
    assert alert.update is AlertUpdate.UNKNOWN


def test_rank_follows_the_amcs_hierarchy():
    ranked = [
        AlertPriority.GEA,
        AlertPriority.EMERGENCY,
        AlertPriority.ALARM,
        AlertPriority.WARNING,
        AlertPriority.CAUTION,
        AlertPriority.EVENT,
    ]

    assert [priority.rank for priority in ranked] == sorted(
        (priority.rank for priority in ranked), reverse=True
    )
    assert len({priority.rank for priority in ranked}) == len(ranked)
    assert AlertPriority.UNKNOWN.rank == AlertPriority.WARNING.rank
