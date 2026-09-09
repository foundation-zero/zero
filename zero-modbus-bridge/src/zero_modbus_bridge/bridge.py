"""Core bridge: Modbus TCP → MQTT using ModbusReader + MqttPublisher."""

import asyncio
import logging
from typing import Any

from faststream.mqtt import MQTTBroker
from pyModbusTCP.client import ModbusClient
from zmqtt import MQTTDisconnectedError, MQTTTimeoutError

from zero_modbus_bridge.io import ModbusTopic
from zero_modbus_bridge.publisher import MqttPublisher, TopicPublisher
from zero_modbus_bridge.reader import ModbusReader
from zero_modbus_bridge.settings import ModbusSettings

logger = logging.getLogger(__name__)

# Transient failures worth dropping and retrying next probe; other MQTTErrors
# (auth, protocol, invalid topic) are misconfigs that must surface.
_TRANSIENT_PUBLISH_ERRORS = (MQTTDisconnectedError, MQTTTimeoutError)


class ModbusBridge:
    """Lightweight entrypoint composing ``ModbusReader`` and a topic publisher."""

    def __init__(
        self,
        reader: ModbusReader,
        publisher: TopicPublisher,
        topics: list[ModbusTopic],
        probe_interval: float = 10.0,
        *,
        drop_failed_publishes: bool = False,
    ):
        """``drop_failed_publishes`` drops a publish that fails with a transient
        broker error (see ``_TRANSIENT_PUBLISH_ERRORS``); the default raises."""
        self._reader = reader
        self._publisher = publisher
        if probe_interval <= 0:
            raise ValueError("probe_interval must be > 0")
        self._probe_interval = probe_interval
        self._drop_failed_publishes = drop_failed_publishes

    @staticmethod
    def from_settings(
        modbus_settings: ModbusSettings,
        broker: MQTTBroker,
        topics: list[ModbusTopic],
    ) -> "ModbusBridge":
        reader = ModbusReader(modbus_settings.modbus_client(), topics)
        publisher = MqttPublisher(broker, topics)
        return ModbusBridge(
            reader,
            publisher,
            topics,
            modbus_settings.modbus_probe_interval,
        )

    @classmethod
    def from_address(
        cls,
        host: str,
        port: int,
        publisher: TopicPublisher,
        topics: list[ModbusTopic],
        probe_interval: float = 10.0,
        *,
        modbus_timeout: float | None = None,
        drop_failed_publishes: bool = False,
    ) -> "ModbusBridge":
        """Bridge sharing a publisher while dialing its own gateway address.

        ``modbus_timeout`` caps each blocking connect/read (``None`` = 30s
        default); keep it below the probe interval so a stall can't overrun.
        """
        client_kwargs: dict[str, Any] = {"auto_open": False}
        if modbus_timeout is not None:
            if modbus_timeout <= 0:
                raise ValueError("modbus_timeout must be > 0")
            client_kwargs["timeout"] = modbus_timeout
        reader = ModbusReader(ModbusClient(host, port, **client_kwargs), topics)
        return cls(
            reader,
            publisher,
            topics,
            probe_interval,
            drop_failed_publishes=drop_failed_publishes,
        )

    async def run(self) -> None:
        loop = asyncio.get_running_loop()
        next_probe_at = loop.time()
        while True:
            await self.run_once()
            next_probe_at += self._probe_interval
            await asyncio.sleep(max(0.0, next_probe_at - loop.time()))

    async def run_once(self) -> None:
        # One worker-thread call per probe: keeps the loop responsive to MQTT
        # keepalives, and the client on one thread (pyModbusTCP isn't thread-safe).
        readings = await asyncio.to_thread(self._probe)
        if readings is None:
            logger.warning("Modbus connection not available - skipping probe")
            return
        dropped = 0
        last_error: BaseException | None = None
        for topic_name, payload in readings:
            try:
                await self._publisher.publish(topic_name, payload)
            except _TRANSIENT_PUBLISH_ERRORS as exc:
                # No retry: at this cadence the next probe supersedes the sample.
                if not self._drop_failed_publishes:
                    raise
                dropped += 1
                last_error = exc
        if dropped:
            # One line per probe, not a traceback per topic: an outage drops all.
            logger.warning(
                "Dropped %d publish(es) this probe (broker unavailable?): %s",
                dropped,
                last_error,
            )

    def _probe(self) -> list[tuple[str, Any]] | None:
        """Run the blocking Modbus probe; ``None`` means the gateway is down.

        ``read_all()`` reopens per topic, so the up-front ``ensure_open`` only
        tells a dead gateway (skip the probe) from a mid-cycle drop (skip the
        rest); it doesn't re-dial a live socket.
        """
        if not self._reader.ensure_open():
            return None
        return list(self._reader.read_all())
