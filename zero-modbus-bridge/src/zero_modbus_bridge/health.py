"""``/health`` for the bridge apps (docs/adr/0001-dependency-outages.md).

The charts point readiness and the restart after 15 minutes not ready at it.
Kubernetes discards the body of an HTTP probe response, so the reason a pod is
not ready is only in the logs: one line each time readiness changes.
"""

import logging
from collections.abc import Awaitable, Callable, Sequence

from faststream.asgi import AsgiFastStream, AsgiResponse, HttpHandler, get
from faststream.asgi.types import Scope
from faststream.mqtt import MQTTBroker

from zero_modbus_bridge.bridge import ModbusBridge

logger = logging.getLogger(__name__)

HEALTH_PORT = 8080
# Below the charts' probe timeoutSeconds (5), so a silent broker gets a 500 and a
# logged reason instead of a probe timeout.
PING_TIMEOUT_SECONDS = 4.0


def make_health_asgi(
    broker: MQTTBroker, required_bridges: Sequence[ModbusBridge] = ()
) -> HttpHandler:
    """204 while the broker answers a ping and every required bridge reads its
    gateway, 500 otherwise."""
    last_reason: str | None = None

    @get(include_in_schema=False)
    async def health(scope: Scope) -> AsgiResponse:
        nonlocal last_reason
        problems = []
        if not await broker.ping(PING_TIMEOUT_SECONDS):
            problems.append("mqtt: broker not connected or not answering pings")
        if not all(bridge.has_read_recently() for bridge in required_bridges):
            problems.append("modbus: no reading in the last 3 probe intervals")
        reason = "; ".join(problems)
        if reason != last_reason:
            if reason:
                logger.warning("Not ready: %s", reason)
            else:
                logger.info("Ready")
            last_reason = reason
        return AsgiResponse(b"", 500 if reason else 204)

    return health


async def run_with_health(
    broker: MQTTBroker,
    after_startup: Callable[[], Awaitable[None]],
    *,
    required_bridges: Sequence[ModbusBridge] = (),
) -> None:
    """Run ``after_startup`` once the broker is connected, serving ``/health``
    on ``HEALTH_PORT`` from the start."""
    app = AsgiFastStream(
        broker,
        asgi_routes=[("/health", make_health_asgi(broker, required_bridges))],
        after_startup=[after_startup],
    )
    # uvicorn listens on 127.0.0.1 by default, which the kubelet can't reach;
    # an access log would log every probe. FastStream parses access_log as a
    # CLI string.
    await app.run(
        run_extra_options={
            "host": "0.0.0.0",
            "port": HEALTH_PORT,
            "access_log": "false",
        }
    )
