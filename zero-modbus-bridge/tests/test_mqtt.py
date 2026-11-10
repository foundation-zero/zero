from typing import NoReturn
from unittest.mock import AsyncMock

import pytest
import zmqtt
from zmqtt import MQTTConnectError, ReconnectConfig

from zero_modbus_bridge.mqtt import (
    REFUSAL_GRACE_SECONDS,
    RefusalRetryingBroker,
    RefusalRetryingClient,
)

NOT_AUTHORIZED = 0x87


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
def client(clock: FakeClock) -> RefusalRetryingClient:
    return RefusalRetryingClient(
        clock=clock,
        exit_process=_exit,
        host="broker",
        reconnect=ReconnectConfig(initial_delay=0, max_attempts=None),
    )


async def test_refusal_is_retried(client: RefusalRetryingClient, attempt: AsyncMock):
    """zmqtt alone would give up on the first CONNACK refusal."""
    attempt.side_effect = [MQTTConnectError(NOT_AUTHORIZED), None]
    await client._connect_with_retry()
    assert attempt.await_count == 2


async def test_refusal_becomes_a_retryable_error(
    client: RefusalRetryingClient, attempt: AsyncMock
):
    attempt.side_effect = MQTTConnectError(NOT_AUTHORIZED)
    with pytest.raises(ConnectionRefusedError, match=r"return code 135"):
        await client._connect()


async def test_exits_when_still_refused_after_grace(
    client: RefusalRetryingClient, attempt: AsyncMock, clock: FakeClock
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
    client: RefusalRetryingClient, attempt: AsyncMock, clock: FakeClock
):
    attempt.side_effect = [MQTTConnectError(NOT_AUTHORIZED), None]
    with pytest.raises(ConnectionRefusedError):
        await client._connect()
    await client._connect()

    clock.now = REFUSAL_GRACE_SECONDS
    attempt.side_effect = MQTTConnectError(NOT_AUTHORIZED)
    with pytest.raises(ConnectionRefusedError):
        await client._connect()


async def test_broker_connects_through_refusal_retrying_client(
    monkeypatch: pytest.MonkeyPatch,
):
    connect = AsyncMock()
    monkeypatch.setattr(RefusalRetryingClient, "connect", connect)
    broker = RefusalRetryingBroker("broker:1883")

    await broker.connect()
    connect.assert_awaited_once()
