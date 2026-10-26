"""Core bridge: Modbus TCP → MQTT using ModbusReader + MqttPublisher."""

import asyncio
import logging
from collections import deque
from datetime import UTC, datetime
from typing import Any

from faststream.mqtt import MQTTBroker
from pydantic import BaseModel
from pyModbusTCP.client import ModbusClient
from zmqtt import MQTTDisconnectedError, MQTTPublishError, MQTTTimeoutError

from zero_modbus_bridge.io import ModbusTopic
from zero_modbus_bridge.publisher import MqttPublisher, TopicPublisher
from zero_modbus_bridge.reader import ModbusReader
from zero_modbus_bridge.settings import ModbusSettings

logger = logging.getLogger(__name__)

# Failures that buffer the message for replay; other MQTTErrors (auth,
# protocol, invalid topic) are misconfigs that must surface.
TRANSIENT_PUBLISH_ERRORS = (
    MQTTPublishError,
    MQTTDisconnectedError,
    MQTTTimeoutError,
)

type _Reading = tuple[str, BaseModel, datetime]


class ModbusBridge:
    """Lightweight entrypoint composing ``ModbusReader`` and a topic publisher."""

    def __init__(
        self,
        reader: ModbusReader,
        publisher: TopicPublisher,
        topics: list[ModbusTopic],
        probe_interval: float = 10.0,
        *,
        buffer_size: int,
    ):
        """``buffer_size`` bounds the in-memory queue of readings whose publish
        failed with a transient broker error (see ``TRANSIENT_PUBLISH_ERRORS``).
        They are replayed in order, with their original read time, once the
        broker accepts again; when the queue is full the oldest is dropped."""
        if buffer_size <= 0:
            raise ValueError("buffer_size must be > 0")
        self._buffer_size = buffer_size
        self._buffer: deque[_Reading] = deque()
        self._dropped = 0
        self._failing = False
        self._reader = reader
        self._publisher = publisher
        if probe_interval <= 0:
            raise ValueError("probe_interval must be > 0")
        self._probe_interval = probe_interval

    @property
    def buffered_count(self) -> int:
        """Readings currently waiting for the broker to accept them."""
        return len(self._buffer)

    @property
    def dropped_count(self) -> int:
        """Readings discarded because the buffer was full, since start."""
        return self._dropped

    @staticmethod
    def from_settings(
        modbus_settings: ModbusSettings,
        broker: MQTTBroker,
        topics: list[ModbusTopic],
        *,
        buffer_size: int,
    ) -> "ModbusBridge":
        reader = ModbusReader(modbus_settings.modbus_client(), topics)
        publisher = MqttPublisher(broker, topics)
        return ModbusBridge(
            reader,
            publisher,
            topics,
            modbus_settings.modbus_probe_interval,
            buffer_size=buffer_size,
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
        buffer_size: int,
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
            buffer_size=buffer_size,
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
        # Replay the backlog before queueing this probe, so a full buffer only
        # drops readings while the broker is still refusing.
        drained = await self._flush()
        if readings is None:
            logger.warning("Modbus connection not available - skipping probe")
        else:
            self._enqueue(readings)
        if drained:
            await self._flush()

    def _enqueue(self, readings: list[_Reading]) -> None:
        dropped = 0
        for reading in readings:
            if len(self._buffer) >= self._buffer_size:
                self._buffer.popleft()
                dropped += 1
            self._buffer.append(reading)
        if dropped:
            self._dropped += dropped
            logger.warning(
                "Buffer full (%d): dropped the %d oldest reading(s), %d dropped in total",
                self._buffer_size,
                dropped,
                self._dropped,
            )

    async def _flush(self) -> bool:
        """Publish buffered readings oldest first; stop at the first failure.

        Returns whether the buffer was drained."""
        replayed = 0
        while self._buffer:
            topic_name, payload, read_at = self._buffer[0]
            try:
                await self._publisher.publish(topic_name, payload, read_at)
            except TRANSIENT_PUBLISH_ERRORS as exc:
                logger.warning(
                    "Publish failed (broker unavailable?), %d reading(s) buffered, "
                    "%d dropped in total: %r",
                    len(self._buffer),
                    self._dropped,
                    exc,
                )
                self._failing = True
                return False
            self._buffer.popleft()
            replayed += 1
        if self._failing:
            logger.info("Broker accepting again: replayed %d reading(s)", replayed)
            self._failing = False
        return True

    def _probe(self) -> list[_Reading] | None:
        """Run the blocking Modbus probe; ``None`` means the gateway is down.

        Each reading is stamped when the lazy ``read_all()`` yields it, i.e.
        right after its registers were read.

        ``read_all()`` reopens per topic, so the up-front ``ensure_open`` only
        tells a dead gateway (skip the probe) from a mid-cycle drop (skip the
        rest); it doesn't re-dial a live socket.
        """
        if not self._reader.ensure_open():
            return None
        return [
            (topic_name, payload, datetime.now(UTC))
            for topic_name, payload in self._reader.read_all()
        ]
