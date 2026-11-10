"""MQTT broker that rides out broker outages (docs/adr/0001-dependency-outages.md)."""

import logging
import os
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, NoReturn

import zmqtt
from faststream.mqtt import MQTTBroker
from zmqtt import MQTTConnectError

logger = logging.getLogger(__name__)

TERMINATION_LOG = Path("/dev/termination-log")

# In the 2026-10-13 cutover RabbitMQ refused logins (CONNACK 0x87, not
# authorized) for up to about a minute after it booted.
REFUSAL_GRACE_SECONDS = 90.0


def exit_with_reason(reason: str) -> NoReturn:
    """Exit at once with ``reason`` as the container's termination message.

    ``os._exit`` because this runs inside client tasks, where a ``SystemExit``
    would start a graceful shutdown that waits on the very client that failed.
    """
    logger.critical("Exiting: %s", reason)
    try:
        TERMINATION_LOG.write_text(reason)
    except OSError:
        logger.debug("No %s to write to (not in Kubernetes?)", TERMINATION_LOG)
    logging.shutdown()
    os._exit(1)


class RefusalRetryingClient(zmqtt.MQTTClient):
    """zmqtt client that retries CONNACK refusals for a while before exiting.

    TODO(ZERO-2532): remove once zMQTT#129 is released. Today a refusal ends
    zmqtt's reconnect task even with max_attempts=None; replace this with
    ReconnectConfig(retry_refusal=lambda e: e.is_transient or e.return_code in {0x05, 0x87}).
    https://github.com/faststream-community/zMQTT/issues/128
    """

    def __init__(
        self,
        *,
        clock: Callable[[], float] = time.monotonic,
        exit_process: Callable[[str], NoReturn] = exit_with_reason,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._clock = clock
        self._exit_process = exit_process
        self._first_refusal_at: float | None = None

    async def _connect(self) -> None:
        """One attempt; zmqtt calls it for the initial connect and every reconnect."""
        try:
            await super()._connect()
        except MQTTConnectError as exc:
            self._on_refused(exc)
        self._first_refusal_at = None

    def _on_refused(self, exc: MQTTConnectError) -> NoReturn:
        reason = f"CONNACK refused (return code {exc.return_code})"
        now = self._clock()
        if self._first_refusal_at is None:
            self._first_refusal_at = now
        if now - self._first_refusal_at >= REFUSAL_GRACE_SECONDS:
            self._exit_process(
                f"mqtt: {reason}, still refused after {REFUSAL_GRACE_SECONDS:g} s"
            )
        logger.warning("MQTT %s, retrying", reason)
        # zmqtt retries OSErrors with its normal backoff.
        raise ConnectionRefusedError(reason) from exc


class RefusalRetryingBroker(MQTTBroker):
    """FastStream broker on a ``RefusalRetryingClient``."""

    async def _connect(self) -> zmqtt.MQTTClient:
        # Same as MQTTBroker._connect, with our client class.
        client = RefusalRetryingClient(**self._connection_kwargs)
        await client.connect()
        self.config.connect(client)
        return client
