"""MQTT broker that rides out broker outages (docs/adr/0001-dependency-outages.md)."""

import asyncio
import logging
import time
from collections.abc import Callable
from secrets import token_hex
from typing import Any, NoReturn

import zmqtt
from faststream.mqtt import MQTTBroker, ReconnectConfig
from faststream.security import SASLPlaintext
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from zero_health import Check, exit_with_reason
from zmqtt import (
    MQTTConnectError,
    MQTTDisconnectedError,
    MQTTProtocolError,
    MQTTTimeoutError,
)

logger = logging.getLogger(__name__)

# In the 2026-10-13 cutover RabbitMQ refused logins (CONNACK 0x87, not
# authorized) for up to about a minute after it booted.
REFUSAL_GRACE_SECONDS = 90.0


class MqttSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    mqtt_host: str
    mqtt_port: int
    mqtt_username: str | None = None
    mqtt_password: str | None = None
    mqtt_client_id: str = Field(default_factory=lambda: f"zero-{token_hex(4)}")

    def make_broker(self, name: str = "mqtt") -> RecoveringBroker:
        """A broker that rides out outages; ``name`` labels it in logs and exit reasons."""

        async def exit_on_give_up() -> None:
            exit_with_reason(f"{name}: client gave up reconnecting")

        security = None
        if self.mqtt_username and self.mqtt_password:
            security = SASLPlaintext(self.mqtt_username, self.mqtt_password)
        return RecoveringBroker(
            f"{self.mqtt_host}:{self.mqtt_port}",
            name=name,
            client_id=self.mqtt_client_id,
            security=security,
            # Retry for as long as it takes, at most 30 s apart, so we are back
            # within about 30 s of the broker.
            reconnect=ReconnectConfig(max_attempts=None, max_delay=30.0),
            # 60 s races RabbitMQ's keepalive window.
            keepalive=15,
            on_connection_recovery_failed=exit_on_give_up,
        )


def broker_check(broker: MQTTBroker) -> Check:
    """Ready while ``broker`` answers a ping."""

    async def check() -> str | None:
        return None if await broker.ping() else "ping failed"

    return check


class RecoveringClient(zmqtt.MQTTClient):
    """zmqtt client that retries what zmqtt gives up on, and exits when it can't.

    TODO(ZERO-2532): drop the refusal handling once zMQTT#129 is released.
    Today a refusal ends zmqtt's reconnect task even with max_attempts=None;
    replace it with ReconnectConfig(retry_refusal=lambda e: e.is_transient or
    e.return_code in {0x05, 0x87}).
    https://github.com/faststream-community/zMQTT/issues/128
    """

    def __init__(
        self,
        *,
        name: str = "mqtt",
        clock: Callable[[], float] = time.monotonic,
        exit_process: Callable[[str], NoReturn] = exit_with_reason,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._name = name
        self._clock = clock
        self._exit_process = exit_process
        self._first_refusal_at: float | None = None

    async def _connect(self) -> None:
        """One attempt; zmqtt calls it for the initial connect and every reconnect."""
        try:
            await super()._connect()
        except MQTTConnectError as exc:
            self._on_refused(exc)
        except OSError, MQTTTimeoutError:
            self._first_refusal_at = None
            raise
        except (MQTTDisconnectedError, MQTTProtocolError) as exc:
            # The broker closed the socket or answered with something other
            # than CONNACK. zmqtt retries only OSErrors.
            self._first_refusal_at = None
            raise ConnectionResetError(f"{type(exc).__name__}: {exc}") from exc
        self._first_refusal_at = None

    async def _run_loop(self) -> None:
        # zmqtt doesn't restart a run loop that fails on a live connection,
        # which would leave the app running without a client.
        try:
            await super()._run_loop()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            self._exit_process(
                f"{self._name}: client stopped: {type(exc).__name__}: {exc}"
            )

    def _on_refused(self, exc: MQTTConnectError) -> NoReturn:
        reason = f"CONNACK refused (return code {exc.return_code})"
        now = self._clock()
        if self._first_refusal_at is None:
            self._first_refusal_at = now
        if now - self._first_refusal_at >= REFUSAL_GRACE_SECONDS:
            self._exit_process(
                f"{self._name}: {reason}, still refused after {REFUSAL_GRACE_SECONDS:g} s"
            )
        logger.warning("%s: %s, retrying", self._name, reason)
        # zmqtt retries OSErrors with its normal backoff.
        raise ConnectionRefusedError(reason) from exc


class RecoveringBroker(MQTTBroker):
    """FastStream broker on a ``RecoveringClient``."""

    def __init__(self, url: str, *, name: str = "mqtt", **kwargs: Any):
        super().__init__(url, **kwargs)
        self._name = name

    async def _connect(self) -> zmqtt.MQTTClient:
        # Same as MQTTBroker._connect, with our client class.
        client = RecoveringClient(name=self._name, **self._connection_kwargs)
        await client.connect()
        self.config.connect(client)
        return client
