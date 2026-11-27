from zero_alert_forwarder.asyncapi import build_asyncapi
from zero_alert_forwarder.mqtt import ALARM_LIST_TOPIC


def test_describes_the_alarm_list_topic():
    spec = build_asyncapi()

    [channel] = spec["channels"].values()
    [operation] = spec["operations"].values()
    assert channel["address"] == ALARM_LIST_TOPIC
    assert operation["action"] == "send"


def test_every_reference_resolves():
    spec = build_asyncapi()

    references = _references(spec)

    assert references
    assert all(_resolve(spec, reference) is not None for reference in references)
    assert {"Alarm", "AlarmListMessage", "AlertPriority", "AlertUpdate"} <= spec[
        "components"
    ]["schemas"].keys()


def _resolve(spec: dict, reference: str) -> object:
    node: object = spec
    for segment in reference.removeprefix("#/").split("/"):
        node = node.get(segment) if isinstance(node, dict) else None
    return node


def _references(node: object) -> set[str]:
    match node:
        # pyrefly: ignore[not-callable]
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
