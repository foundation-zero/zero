"""MQTT broker that rides out broker outages (docs/adr/0001-dependency-outages.md).

TODO(ZERO-2406): zero-atpx-nmea has a copy of this module; phase 2 moves both
into packages/py/zero-mqtt.
"""

import asyncio
import logging
import os
import time
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from typing import Any, NoReturn

import zmqtt
from faststream.mqtt import MQTTBroker
from zmqtt import (
    MQTTConnectError,
    MQTTDisconnectedError,
    MQTTProtocolError,
)

from zero_modbus_bridge.logs import log_prefix

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
    """zmqtt client that retries refusals for a while and exits if its run loop dies.

    zmqtt retries a refused CONNACK when ``retry_refusal`` says so. This client
    says so until the refusals have gone on for ``REFUSAL_GRACE_SECONDS``. Then
    it exits with the refusal as the termination message, on the first connect
    and on a reconnect alike.

    TODO(ZERO-2532): drop the handshake and run loop handling once zMQTT#137
    is released.
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
        self._reconnect = replace(self._reconnect, retry_refusal=self._retry_refusal)
        self._name = name
        self._clock = clock
        self._exit_process = exit_process
        self._refused_since: float | None = None

    async def _connect(self) -> None:
        """One attempt; zmqtt calls it for the initial connect and every reconnect."""
        # Anything but another refusal restarts the grace period.
        refused_since, self._refused_since = self._refused_since, None
        try:
            await super()._connect()
        except MQTTConnectError:
            self._refused_since = refused_since
            raise
        except (MQTTDisconnectedError, MQTTProtocolError) as exc:
            # The broker closed the socket or answered with something other
            # than CONNACK. zmqtt doesn't retry those.
            raise ConnectionResetError(f"{type(exc).__name__}: {exc}") from exc

    def _retry_refusal(self, refusal: MQTTConnectError) -> bool:
        now = self._clock()
        if self._refused_since is None:
            self._refused_since = now
        if now - self._refused_since >= REFUSAL_GRACE_SECONDS:
            # Exit here rather than return False: zmqtt's own give-up loses the
            # refusal (the reconnect path only says "gave up reconnecting", the
            # first connect raises without a termination message).
            self._exit_process(
                f"{self._name}: CONNACK refused {refusal.return_code:#04x}, "
                f"still refused after {REFUSAL_GRACE_SECONDS:.0f} s"
            )
        return True

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


class RecoveringBroker(MQTTBroker):
    """FastStream broker on a ``RecoveringClient``."""

    def __init__(self, url: str, *, name: str = "mqtt", **kwargs: Any):
        super().__init__(url, **kwargs)
        self._name = name

    async def _connect(self) -> zmqtt.MQTTClient:
        # Same as MQTTBroker._connect, with our client class.
        client = RecoveringClient(name=self._name, **self._connection_kwargs)
        # The run loop started here keeps the prefix through every reconnect.
        with log_prefix(self._name):
            await client.connect()
        self.config.connect(client)
        return client
