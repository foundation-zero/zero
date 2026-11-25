from typing import Any

from faststream.mqtt import MQTTBroker
from faststream.specification import AsyncAPI

from zero_alert_forwarder.mqtt import alarm_list_publisher


def build_asyncapi(
    title: str = "AMCS alarms", version: str = "1.0.0"
) -> dict[str, Any]:
    """The AsyncAPI 3.0 document of what the forwarder publishes, for zero-mqtt-graphql.

    Built from the same publisher the forwarder registers, so spec and runtime cannot drift.
    """
    broker = MQTTBroker("localhost:1883")
    alarm_list_publisher(broker)
    return (
        AsyncAPI(broker, title=title, version=version).to_specification().to_jsonable()
    )
