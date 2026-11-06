from typing import NoReturn
from unittest.mock import AsyncMock

import pytest
import zmqtt
from zmqtt import MQTTConnectError, ReconnectConfig

from tests.test_readiness import Exited, FakeClock
from zero_modbus_bridge.mqtt import (
    REFUSAL_GRACE_SECONDS,
    ReportingBroker,
    ReportingClient,
)
from zero_modbus_bridge.readiness import Readiness

NOT_AUTHORIZED = 0x87


def _exit(reason: str) -> NoReturn:
    raise Exited(reason)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def readiness(clock: FakeClock) -> Readiness:
    return Readiness(None, clock=clock, exit_process=_exit)


@pytest.fixture
def attempt(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Stands in for one zmqtt connect attempt."""
    connect = AsyncMock()
    monkeypatch.setattr(zmqtt.MQTTClient, "_connect", connect)
    return connect


@pytest.fixture
def client(readiness: Readiness, clock: FakeClock) -> ReportingClient:
    return ReportingClient(
        readiness,
        clock=clock,
        host="broker",
        reconnect=ReconnectConfig(initial_delay=0, max_attempts=None),
    )


async def test_connected_is_ready(
    client: ReportingClient, readiness: Readiness, attempt: AsyncMock
):
    await client._connect_with_retry()
    assert readiness.status == "ready"


async def test_unreachable_broker_is_not_ready(
    client: ReportingClient, readiness: Readiness, attempt: AsyncMock
):
    attempt.side_effect = ConnectionRefusedError(111, "Connect call failed")
    with pytest.raises(ConnectionRefusedError):
        await client._connect()
    assert readiness.status.endswith(
        ": mqtt: ConnectionRefusedError: [Errno 111] Connect call failed"
    )


async def test_refusal_is_retried(
    client: ReportingClient, readiness: Readiness, attempt: AsyncMock
):
    """zmqtt alone would give up on the first CONNACK refusal."""
    attempt.side_effect = [MQTTConnectError(NOT_AUTHORIZED), None]
    await client._connect_with_retry()
    assert attempt.await_count == 2
    assert readiness.status == "ready"


async def test_refusal_reported_as_not_ready(
    client: ReportingClient, readiness: Readiness, attempt: AsyncMock
):
    attempt.side_effect = MQTTConnectError(NOT_AUTHORIZED)
    with pytest.raises(ConnectionRefusedError):
        await client._connect()
    assert readiness.status.endswith(": mqtt: CONNACK refused (return code 135)")


async def test_exits_when_still_refused_after_grace(
    client: ReportingClient, attempt: AsyncMock, clock: FakeClock
):
    attempt.side_effect = MQTTConnectError(NOT_AUTHORIZED)
    with pytest.raises(ConnectionRefusedError):
        await client._connect()

    clock.now = REFUSAL_GRACE_SECONDS
    with pytest.raises(
        Exited, match="mqtt: CONNACK refused .* still refused after 90 s"
    ):
        await client._connect()


async def test_refusal_grace_restarts_after_connecting(
    client: ReportingClient, attempt: AsyncMock, clock: FakeClock
):
    attempt.side_effect = [MQTTConnectError(NOT_AUTHORIZED), None]
    with pytest.raises(ConnectionRefusedError):
        await client._connect()
    await client._connect()

    clock.now = REFUSAL_GRACE_SECONDS
    attempt.side_effect = MQTTConnectError(NOT_AUTHORIZED)
    with pytest.raises(ConnectionRefusedError):
        await client._connect()


async def test_broker_connects_through_reporting_client(
    monkeypatch: pytest.MonkeyPatch, readiness: Readiness
):
    connect = AsyncMock()
    monkeypatch.setattr(ReportingClient, "connect", connect)
    broker = ReportingBroker("broker:1883", readiness)

    await broker.connect()
    connect.assert_awaited_once()
