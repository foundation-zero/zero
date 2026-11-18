"""`/health` for the readiness probe (docs/adr/0001-dependency-outages.md).

The reason a pod is not ready is in zmqtt's log, which names the broker.
"""

import asyncio

from faststream.asgi import AsgiResponse, HttpHandler, get
from faststream.mqtt import MQTTBroker

# Below the probe's timeoutSeconds in the chart.
PING_TIMEOUT_SECONDS = 4.0


def make_health_asgi(*brokers: MQTTBroker) -> HttpHandler:
    """204 while every broker answers a ping, else 500.

    FastStream's `make_ping_asgi` pings only one broker."""

    @get(include_in_schema=False)
    async def health(scope: object) -> AsgiResponse:
        async with asyncio.TaskGroup() as tg:
            pings = [
                tg.create_task(broker.ping(PING_TIMEOUT_SECONDS)) for broker in brokers
            ]
        ready = all(ping.result() for ping in pings)
        return AsgiResponse(b"", 204 if ready else 500)

    return health
