import asyncio
import contextlib
import socket
from unittest.mock import AsyncMock, MagicMock

import pytest
from faststream.asgi import make_ping_asgi
from faststream.mqtt import ReconnectConfig

from zero_modbus_bridge import health
from zero_modbus_bridge.health import make_health_asgi, run_with_health
from zero_modbus_bridge.mqtt import RecoveringBroker


async def _probe(handler) -> int:
    """GET the handler like the kubelet does and return the status code."""
    sent = []

    async def send(message):
        sent.append(message)

    scope = {"type": "http", "method": "GET", "path": "/health", "headers": []}
    await handler(scope, AsyncMock(), send)
    return sent[0]["status"]


def _broker(*, answers: bool) -> MagicMock:
    return MagicMock(ping=AsyncMock(return_value=answers))


def _bridge(*, reading: bool) -> MagicMock:
    return MagicMock(has_read_recently=MagicMock(return_value=reading))


@pytest.mark.parametrize(
    ("answers", "reading", "status"),
    [(True, True, 204), (False, True, 500), (True, False, 500)],
)
async def test_ready_while_broker_answers_and_gateway_reads(answers, reading, status):
    broker = _broker(answers=answers)
    handler = make_health_asgi(broker, _bridge(reading=reading))

    assert await _probe(handler) == status


async def test_pings_with_a_timeout_below_the_probe_timeout():
    broker = _broker(answers=True)

    await _probe(make_health_asgi(broker, _bridge(reading=True)))

    broker.ping.assert_awaited_once_with(4.0)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


async def _health_status(port: int) -> int:
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    writer.write(b"GET /health HTTP/1.1\r\nHost: test\r\nConnection: close\r\n\r\n")
    status_line = await reader.readline()
    writer.close()
    return int(status_line.split()[1])


async def test_serves_health_while_the_broker_is_unreachable(
    monkeypatch: pytest.MonkeyPatch,
):
    port = _free_port()
    monkeypatch.setattr(health, "HEALTH_PORT", port)
    broker = RecoveringBroker(
        f"127.0.0.1:{_free_port()}", reconnect=ReconnectConfig(max_attempts=None)
    )

    async def after_startup() -> None:
        raise AssertionError("ran without a broker")

    server = asyncio.create_task(
        run_with_health(broker, after_startup, make_ping_asgi(broker, timeout=1.0))
    )
    try:
        for _ in range(50):
            try:
                assert await _health_status(port) == 500
                break
            except ConnectionRefusedError:
                await asyncio.sleep(0.1)
        else:
            pytest.fail("/health never came up")
    finally:
        server.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await server
