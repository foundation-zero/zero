"""`/health` for the Kubernetes probes (docs/adr/0001-dependency-outages.md).

Kubernetes discards the bodies of HTTP probes, so the reason a pod is not
ready goes to the log instead, once per change.
"""

import asyncio
import logging

from faststream.asgi import AsgiResponse, HttpHandler, get
from faststream.mqtt import MQTTBroker

logger = logging.getLogger(__name__)

# Below the probes' timeoutSeconds in the chart.
PING_TIMEOUT_SECONDS = 4.0


def make_health_asgi(brokers: dict[str, MQTTBroker]) -> HttpHandler:
    """204 while every broker answers a ping, else 500.

    ``brokers`` maps the name used in the log to the broker."""
    healthy = AsgiResponse(b"", 204)
    unhealthy = AsgiResponse(b"", 500)
    last_down: list[str] | None = None

    @get(include_in_schema=False)
    async def health(scope: object) -> AsgiResponse:
        nonlocal last_down
        async with asyncio.TaskGroup() as tg:
            pings = {
                name: tg.create_task(broker.ping(PING_TIMEOUT_SECONDS))
                for name, broker in brokers.items()
            }
        down = [name for name, ping in pings.items() if not ping.result()]

        if down != last_down:
            if down:
                logger.warning(f"Not ready: {', '.join(down)} did not answer a ping")
            else:
                logger.info(f"Ready: {', '.join(brokers)} answer pings")
            last_down = down

        return unhealthy if down else healthy

    return health
