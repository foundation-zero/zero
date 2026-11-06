"""MQTT broker that reports its connection to ``Readiness`` (docs/adr/0001).

Copied from zero-modbus-bridge, with a dependency name per broker, since this
service needs two.
"""

import time
from collections.abc import Callable
from typing import Any

import zmqtt
from faststream.mqtt import MQTTBroker
from zmqtt import MQTTConnectError, MQTTTimeoutError

from zero_atpx_nmea.readiness import Readiness

# In the 2026-10-13 cutover RabbitMQ refused logins (CONNACK 0x87, not
# authorized) for up to about a minute after it booted.
REFUSAL_GRACE_SECONDS = 90.0


class ReportingClient(zmqtt.MQTTClient):
    """zmqtt client that reports each connect attempt to ``Readiness``."""

    def __init__(
        self,
        readiness: Readiness,
        dependency: str,
        *,
        clock: Callable[[], float] = time.monotonic,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._readiness = readiness
        self._dependency = dependency
        self._clock = clock
        self._first_refusal_at: float | None = None

    async def _connect(self) -> None:
        """One attempt; zmqtt calls it for the initial connect and every reconnect."""
        try:
            await super()._connect()
        except MQTTConnectError as exc:
            self._on_refused(exc)
        except (OSError, MQTTTimeoutError) as exc:
            self._readiness.not_ready(self._dependency, f"{type(exc).__name__}: {exc}")
            raise
        self._first_refusal_at = None
        self._readiness.ready(self._dependency, "connected")

    def _on_refused(self, exc: MQTTConnectError) -> None:
        # TODO: drop this once zmqtt retries CONNACK refusals itself; today a
        # refusal ends its reconnect task even with max_attempts=None.
        # https://github.com/faststream-community/zMQTT/issues/128
        reason = f"CONNACK refused (return code {exc.return_code})"
        self._readiness.not_ready(self._dependency, reason)
        now = self._clock()
        if self._first_refusal_at is None:
            self._first_refusal_at = now
        if now - self._first_refusal_at >= REFUSAL_GRACE_SECONDS:
            self._readiness.exit(
                f"{self._dependency}: {reason}, "
                f"still refused after {REFUSAL_GRACE_SECONDS:g} s"
            )
        # zmqtt retries OSErrors with its normal backoff.
        raise ConnectionRefusedError(reason) from exc


class ReportingBroker(MQTTBroker):
    """FastStream broker on a ``ReportingClient``."""

    def __init__(self, url: str, readiness: Readiness, dependency: str, **kwargs: Any):
        super().__init__(url, **kwargs)
        self._readiness = readiness
        self._dependency = dependency

    async def _connect(self) -> zmqtt.MQTTClient:
        # Same as MQTTBroker._connect, with our client class.
        client = ReportingClient(
            self._readiness, self._dependency, **self._connection_kwargs
        )
        await client.connect()
        self.config.connect(client)
        return client
