"""MQTT broker that rides out broker outages (docs/adr/0001-dependency-outages.md).

TODO(ZERO-2406): copied from zero-modbus-bridge; phase 2 moves both
into packages/py/zero-mqtt.
"""

import asyncio
import logging
import os
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, NoReturn

import zmqtt
from faststream.mqtt import MQTTBroker
from zmqtt import (
    MQTTConnectError,
    MQTTDisconnectedError,
    MQTTProtocolError,
    MQTTTimeoutError,
)

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
