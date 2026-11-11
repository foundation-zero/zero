import asyncio
import re
from typing import NoReturn
from unittest.mock import AsyncMock

import pytest
import zmqtt
from zmqtt import (
    MQTTConnectError,
    MQTTDisconnectedError,
    MQTTProtocolError,
    ReconnectConfig,
)

from zero_mqtt import MqttSettings
from zero_mqtt import broker as broker_module
from zero_mqtt.broker import (
    REFUSAL_GRACE_SECONDS,
    RecoveringBroker,
    RecoveringClient,
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
def client(clock: FakeClock) -> RecoveringClient:
    return RecoveringClient(
        clock=clock,
        exit_process=_exit,
        host="broker",
        reconnect=ReconnectConfig(initial_delay=0, max_attempts=None),
    )


async def test_refusal_is_retried(client: RecoveringClient, attempt: AsyncMock):
    """zmqtt alone would give up on the first CONNACK refusal."""
    attempt.side_effect = [MQTTConnectError(NOT_AUTHORIZED), None]
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


async def test_exits_when_still_refused_after_grace(
    client: RecoveringClient, attempt: AsyncMock, clock: FakeClock
):
    attempt.side_effect = MQTTConnectError(NOT_AUTHORIZED)
    with pytest.raises(ConnectionRefusedError, match=r"return code 135"):
        await client._connect()

    clock.now = REFUSAL_GRACE_SECONDS
    with pytest.raises(
        Exited, match="^mqtt: CONNACK refused .* still refused after 90 s"
    ):
        await client._connect()


async def test_refusal_grace_restarts_after_connecting(
    client: RecoveringClient, attempt: AsyncMock, clock: FakeClock
):
    attempt.side_effect = [MQTTConnectError(NOT_AUTHORIZED), None]
    with pytest.raises(ConnectionRefusedError):
        await client._connect()
    await client._connect()

    clock.now = REFUSAL_GRACE_SECONDS
    attempt.side_effect = MQTTConnectError(NOT_AUTHORIZED)
    with pytest.raises(ConnectionRefusedError):
        await client._connect()


async def test_refusal_grace_restarts_after_another_failure(
    client: RecoveringClient, attempt: AsyncMock, clock: FakeClock
):
    attempt.side_effect = MQTTConnectError(NOT_AUTHORIZED)
    with pytest.raises(ConnectionRefusedError):
        await client._connect()
    attempt.side_effect = ConnectionRefusedError(111, "Connect call failed")
    with pytest.raises(ConnectionRefusedError):
        await client._connect()

    clock.now = REFUSAL_GRACE_SECONDS
    attempt.side_effect = MQTTConnectError(NOT_AUTHORIZED)
    with pytest.raises(ConnectionRefusedError):
        await client._connect()


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


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    monkeypatch.setenv("MQTT_HOST", "localhost")
    monkeypatch.setenv("MQTT_PORT", "1883")
    monkeypatch.delenv("MQTT_CLIENT_ID", raising=False)
    return monkeypatch


def _settings() -> MqttSettings:
    return MqttSettings(_env_file=None)  # type: ignore[call-arg]


def test_mqtt_client_id_default(env: pytest.MonkeyPatch):
    assert re.fullmatch(r"zero-[0-9a-f]{8}", _settings().mqtt_client_id)


def test_mqtt_client_id_from_env(env: pytest.MonkeyPatch):
    env.setenv("MQTT_CLIENT_ID", "custom-id")
    assert _settings().mqtt_client_id == "custom-id"


def test_broker_rides_out_outages(env: pytest.MonkeyPatch):
    broker = _settings().make_broker()
    kwargs = broker._connection_kwargs
    assert isinstance(broker, RecoveringBroker)
    assert kwargs["reconnect"].max_attempts is None
    assert kwargs["reconnect"].max_delay == 30.0
    assert kwargs["keepalive"] == 15


async def test_broker_exits_when_the_client_gives_up(env: pytest.MonkeyPatch):
    env.setattr(broker_module, "exit_with_reason", _exit)
    broker = _settings().make_broker(name="mqtt-input")
    with pytest.raises(Exited, match="^mqtt-input: client gave up reconnecting$"):
        await broker._connection_kwargs["on_connection_recovery_failed"]()


def test_broker_logs_in_with_credentials(env: pytest.MonkeyPatch):
    env.setenv("MQTT_USERNAME", "user")
    env.setenv("MQTT_PASSWORD", "secret")
    kwargs = _settings().make_broker()._connection_kwargs
    assert (kwargs["username"], kwargs["password"]) == ("user", "secret")
