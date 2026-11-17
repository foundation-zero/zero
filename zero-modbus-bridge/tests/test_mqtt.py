import asyncio
import os
from pathlib import Path
from typing import NoReturn
from unittest.mock import AsyncMock, MagicMock

import pytest
import zmqtt
from zmqtt import (
    MQTTConnectError,
    MQTTDisconnectedError,
    MQTTProtocolError,
    ReconnectConfig,
)

from zero_modbus_bridge import mqtt
from zero_modbus_bridge.mqtt import (
    REFUSAL_GRACE_SECONDS,
    RecoveringBroker,
    RecoveringClient,
    exit_with_reason,
)

REFUSED = MQTTConnectError(0x87)  # not authorized
ATTEMPT_INTERVAL = 30.0


class Exited(Exception):
    pass


def _exit(reason: str) -> NoReturn:
    raise Exited(reason)


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def attempt(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Stands in for one zmqtt connect attempt."""
    connect = AsyncMock()
    monkeypatch.setattr(zmqtt.MQTTClient, "_connect", connect)
    return connect


@pytest.fixture
def client(clock: FakeClock) -> RecoveringClient:
    return RecoveringClient(
        clock=clock,
        exit_process=_exit,
        host="broker",
        reconnect=ReconnectConfig(initial_delay=0, max_attempts=None),
    )


def _attempts(clock: FakeClock, *outcomes: Exception | None):
    """Connect attempts ``ATTEMPT_INTERVAL`` apart that end as ``outcomes`` says (``None`` connects).

    Once ``outcomes`` runs out, every attempt is refused."""
    remaining = list(outcomes)

    async def attempt() -> None:
        clock.now += ATTEMPT_INTERVAL
        outcome = remaining.pop(0) if remaining else REFUSED
        if outcome is not None:
            raise outcome

    return attempt


async def test_refusal_is_retried(client: RecoveringClient, attempt: AsyncMock):
    """zmqtt alone would give up on the first "not authorized" refusal."""
    attempt.side_effect = [REFUSED, None]
    await client._connect_with_retry()
    assert attempt.await_count == 2


@pytest.mark.parametrize(
    "error",
    [
        MQTTDisconnectedError("Connection closed by remote"),
        MQTTProtocolError("Expected CONNACK"),
    ],
)
async def test_broken_handshake_is_retried(
    client: RecoveringClient, attempt: AsyncMock, error: Exception
):
    attempt.side_effect = [error, None]
    await client._connect_with_retry()
    assert attempt.await_count == 2


async def test_gives_up_when_still_refused_after_grace(
    client: RecoveringClient, attempt: AsyncMock, clock: FakeClock
):
    attempt.side_effect = _attempts(clock)
    with pytest.raises(MQTTConnectError):
        await client._connect_with_retry()
    refused_for = clock.now - ATTEMPT_INTERVAL  # since the first attempt
    assert refused_for == REFUSAL_GRACE_SECONDS


async def test_refusal_grace_restarts_after_connecting(
    client: RecoveringClient, attempt: AsyncMock, clock: FakeClock
):
    attempt.side_effect = _attempts(clock, REFUSED, REFUSED, None)
    await client._connect_with_retry()

    attempt.side_effect = _attempts(clock, REFUSED, REFUSED, REFUSED, None)
    await client._connect_with_retry()


async def test_refusal_grace_restarts_after_another_failure(
    client: RecoveringClient, attempt: AsyncMock, clock: FakeClock
):
    transport_error = ConnectionRefusedError(111, "Connect call failed")
    attempt.side_effect = _attempts(
        clock, REFUSED, REFUSED, REFUSED, transport_error, REFUSED, REFUSED, None
    )
    await client._connect_with_retry()


async def test_exits_when_refused_past_grace_on_reconnect(
    client: RecoveringClient, attempt: AsyncMock, clock: FakeClock
):
    protocol = MagicMock()
    protocol.run = AsyncMock(side_effect=ConnectionResetError("Connection lost"))
    protocol.started_event.wait = AsyncMock()
    protocol._transport.close = AsyncMock()
    client._protocol = protocol
    attempt.side_effect = _attempts(clock)
    with pytest.raises(Exited, match="^mqtt: client stopped: MQTTConnectError"):
        await client._run_loop()
    assert attempt.await_count == REFUSAL_GRACE_SECONDS / ATTEMPT_INTERVAL + 1


async def test_exits_when_run_loop_fails(
    monkeypatch: pytest.MonkeyPatch, client: RecoveringClient
):
    run_loop = AsyncMock(side_effect=MQTTProtocolError("Unexpected packet"))
    monkeypatch.setattr(zmqtt.MQTTClient, "_run_loop", run_loop)
    with pytest.raises(
        Exited, match="^mqtt: client stopped: MQTTProtocolError: Unexpected packet"
    ):
        await client._run_loop()


async def test_cancelled_run_loop_does_not_exit(
    monkeypatch: pytest.MonkeyPatch, client: RecoveringClient
):
    run_loop = AsyncMock(side_effect=asyncio.CancelledError)
    monkeypatch.setattr(zmqtt.MQTTClient, "_run_loop", run_loop)
    with pytest.raises(asyncio.CancelledError):
        await client._run_loop()


async def test_broker_connects_through_recovering_client(
    monkeypatch: pytest.MonkeyPatch,
):
    connect = AsyncMock()
    monkeypatch.setattr(RecoveringClient, "connect", connect)
    broker = RecoveringBroker("broker:1883")

    await broker.connect()
    connect.assert_awaited_once()


def test_exit_writes_termination_message(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    termination_log = tmp_path / "termination-log"
    monkeypatch.setattr(mqtt, "TERMINATION_LOG", termination_log)
    monkeypatch.setattr(os, "_exit", _exit)
    with pytest.raises(Exited):
        exit_with_reason("mqtt: client gave up reconnecting")
    assert termination_log.read_text() == "mqtt: client gave up reconnecting"
