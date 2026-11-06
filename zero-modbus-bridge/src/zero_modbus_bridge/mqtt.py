"""MQTT broker that reports its connection to ``Readiness`` (docs/adr/0001)."""

import time
from collections.abc import Callable
from typing import Any

import zmqtt
from faststream.mqtt import MQTTBroker
from zmqtt import MQTTConnectError, MQTTTimeoutError

from zero_modbus_bridge.readiness import Readiness

# In the 2026-10-13 cutover RabbitMQ refused logins (CONNACK 0x87, not
# authorized) for up to about a minute after it booted.
REFUSAL_GRACE_SECONDS = 90.0


class ReportingClient(zmqtt.MQTTClient):
    """zmqtt client that reports each connect attempt to ``Readiness``."""

    def __init__(
        self,
        readiness: Readiness,
        *,
        clock: Callable[[], float] = time.monotonic,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._readiness = readiness
        self._clock = clock
        self._first_refusal_at: float | None = None

    async def _connect_with_retry(
        self, *, wait_before_first_attempt: bool = False
    ) -> None:
        # zmqtt waits before the first attempt only after losing a live
        # connection; report that now rather than after the first failed attempt.
        if wait_before_first_attempt:
            self._readiness.not_ready("mqtt", "connection lost")
        await super()._connect_with_retry(
            wait_before_first_attempt=wait_before_first_attempt
        )

    async def _connect(self) -> None:
        """One attempt; zmqtt calls it for the initial connect and every reconnect."""
        try:
            await super()._connect()
        except MQTTConnectError as exc:
            self._on_refused(exc)
        except (OSError, MQTTTimeoutError) as exc:
            self._readiness.not_ready("mqtt", f"{type(exc).__name__}: {exc}")
            raise
        self._first_refusal_at = None
        self._readiness.ready("mqtt")

    def _on_refused(self, exc: MQTTConnectError) -> None:
        # TODO: today a refusal ends zmqtt's reconnect task even with
        # max_attempts=None. Once zMQTT#128 is released, replace this with
        # ReconnectConfig(retry_refusal=lambda e: e.is_transient or e.return_code in {0x05, 0x87}).
        # https://github.com/faststream-community/zMQTT/issues/128
        reason = f"CONNACK refused (return code {exc.return_code})"
        self._readiness.not_ready("mqtt", reason)
        now = self._clock()
        if self._first_refusal_at is None:
            self._first_refusal_at = now
        if now - self._first_refusal_at >= REFUSAL_GRACE_SECONDS:
            self._readiness.exit(
                f"mqtt: {reason}, still refused after {REFUSAL_GRACE_SECONDS:g} s"
            )
        # zmqtt retries OSErrors with its normal backoff.
        raise ConnectionRefusedError(reason) from exc


class ReportingBroker(MQTTBroker):
    """FastStream broker on a ``ReportingClient``."""

    def __init__(self, url: str, readiness: Readiness, **kwargs: Any):
        super().__init__(url, **kwargs)
        self._readiness = readiness

    async def _connect(self) -> zmqtt.MQTTClient:
        # Same as MQTTBroker._connect, with our client class.
        client = ReportingClient(self._readiness, **self._connection_kwargs)
        await client.connect()
        self.config.connect(client)
        return client
