"""``/health`` and ``/live`` for the bridge apps' readiness and liveness probes
(docs/adr/0001-dependency-outages.md).

The reason a pod is not ready is in the logs of zmqtt and the bridge.
"""

from collections.abc import Awaitable, Callable

from faststream.asgi import AsgiFastStream, AsgiResponse, HttpHandler, get
from faststream.asgi.types import Scope
from faststream.mqtt import MQTTBroker

from zero_modbus_bridge.bridge import ModbusBridge

HEALTH_PORT = 8080
# Below the charts' probe timeoutSeconds (5), so a silent broker gets a 500
# instead of a probe timeout.
PING_TIMEOUT_SECONDS = 4.0


def make_health_asgi(broker: MQTTBroker, bridge: ModbusBridge) -> HttpHandler:
    """204 while the bridge reads its gateway and the broker answers a ping, else 500.

    For an app whose gateway is required; otherwise use FastStream's
    ``make_ping_asgi``."""

    @get(include_in_schema=False)
    async def health(scope: Scope) -> AsgiResponse:
        ready = bridge.has_read_recently() and await broker.ping(PING_TIMEOUT_SECONDS)
        return AsgiResponse(b"", 204 if ready else 500)

    return health


@get(include_in_schema=False)
async def live(scope: Scope) -> AsgiResponse:
    """204 whenever it gets to run: the liveness probe restarts a pod whose
    event loop is stuck. It checks no dependency (ADR 0001)."""
    return AsgiResponse(b"", 204)


async def run_with_health(
    broker: MQTTBroker,
    after_startup: Callable[[], Awaitable[None]],
    health: HttpHandler,
) -> None:
    """Run ``after_startup`` once the broker is connected, serving ``health``
    at ``/health`` and ``live`` at ``/live`` on ``HEALTH_PORT`` from the start."""
    app = AsgiFastStream(
        broker,
        asgi_routes=[("/health", health), ("/live", live)],
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
