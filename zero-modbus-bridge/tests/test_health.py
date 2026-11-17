import asyncio
import contextlib
import logging
import socket
from unittest.mock import AsyncMock, MagicMock

import pytest
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


async def test_healthy_when_broker_answers_and_gateway_reads(caplog):
    caplog.set_level(logging.INFO)
    broker = _broker(answers=True)
    handler = make_health_asgi(broker, [_bridge(reading=True)])

    assert await _probe(handler) == 204
    broker.ping.assert_awaited_once_with(4.0)
    assert caplog.messages == ["Ready"]


async def test_broker_down_is_not_ready():
    handler = make_health_asgi(_broker(answers=False), [_bridge(reading=True)])

    assert await _probe(handler) == 500


async def test_gateway_down_is_not_ready():
    handler = make_health_asgi(_broker(answers=True), [_bridge(reading=False)])

    assert await _probe(handler) == 500


async def test_without_required_bridges_only_the_broker_counts():
    assert await _probe(make_health_asgi(_broker(answers=True))) == 204


async def test_logs_only_when_readiness_changes(caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.INFO)
    broker = _broker(answers=True)
    bridge = _bridge(reading=False)
    handler = make_health_asgi(broker, [bridge])

    await _probe(handler)
    await _probe(handler)
    broker.ping.return_value = False
    await _probe(handler)
    broker.ping.return_value = True
    bridge.has_read_recently.return_value = True
    await _probe(handler)
    await _probe(handler)

    assert caplog.messages == [
        "Not ready: modbus: no reading in the last 3 probe intervals",
        "Not ready: mqtt: broker not connected or not answering pings; "
        "modbus: no reading in the last 3 probe intervals",
        "Ready",
    ]


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

    server = asyncio.create_task(run_with_health(broker, after_startup))
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
