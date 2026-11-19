from zero_alert_forwarder.asyncapi import build_asyncapi
from zero_alert_forwarder.mqtt import ALARM_LIST_TOPIC


def test_describes_the_alarm_list_topic():
    spec = build_asyncapi()

    channel = spec["channels"]["alarmList"]
    assert channel["address"] == ALARM_LIST_TOPIC
    assert channel["messages"]["alarmList"]["x-ttl"] == "30s"
    assert spec["operations"]["sendAlarmList"]["action"] == "send"


def test_every_reference_resolves_to_a_component():
    spec = build_asyncapi()
    schemas = spec["components"]["schemas"]

    references = _references(spec)

    assert "#/components/schemas/AlarmListMessage" in references
    assert {
        reference.removeprefix("#/components/schemas/")
        for reference in references
        if reference.startswith("#/components/schemas/")
    } <= schemas.keys()
    assert {"Alarm", "AlertPriority", "AlertUpdate"} <= schemas.keys()


def _references(node: object) -> set[str]:
    match node:
        case {"$ref": str(reference)}:
            return {reference}
        case dict():
            return {
                reference for value in node.values() for reference in _references(value)
            }
        case list():
            return {reference for value in node for reference in _references(value)}
        case _:
            return set()
