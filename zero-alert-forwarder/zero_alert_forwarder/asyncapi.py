"""The AsyncAPI 3.0 document of what the forwarder publishes, for zero-mqtt-graphql."""

from typing import Any

from zero_alert_forwarder.alarm_list import AlarmListMessage
from zero_alert_forwarder.mqtt import ALARM_LIST_TOPIC

SCHEMA_REF_PREFIX = "#/components/schemas/"

# A few publish intervals (at most 10s), so a stopped forwarder empties the list soon.
ALARM_LIST_TTL = "30s"


def build_asyncapi() -> dict[str, Any]:
    payload = AlarmListMessage.model_json_schema(
        ref_template=f"{SCHEMA_REF_PREFIX}{{model}}"
    )
    schemas = payload.pop("$defs", {}) | {AlarmListMessage.__name__: payload}
    return {
        "asyncapi": "3.0.0",
        "info": {"title": "AMCS alarms", "version": "1.0.0"},
        "defaultContentType": "application/json",
        "channels": {
            "alarmList": {
                "address": ALARM_LIST_TOPIC,
                "messages": {
                    "alarmList": {
                        "payload": {
                            "$ref": f"{SCHEMA_REF_PREFIX}{AlarmListMessage.__name__}"
                        },
                        "x-ttl": ALARM_LIST_TTL,
                    }
                },
            }
        },
        "operations": {
            "sendAlarmList": {
                "action": "send",
                "channel": {"$ref": "#/channels/alarmList"},
            }
        },
        "components": {"schemas": schemas},
    }
