"""Core bridge: Modbus TCP → MQTT using ModbusReader + MqttPublisher."""

import asyncio
import logging
import time
from collections import deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from typing import Any

from faststream.mqtt import MQTTBroker
from pydantic import BaseModel
from pyModbusTCP.client import ModbusClient
from zmqtt import MQTTDisconnectedError, MQTTPublishError, MQTTTimeoutError

from zero_modbus_bridge.commands import ModbusCommand
from zero_modbus_bridge.io import ModbusTopic
from zero_modbus_bridge.publisher import MqttPublisher, TopicPublisher
from zero_modbus_bridge.reader import ModbusReader
from zero_modbus_bridge.settings import ModbusSettings
from zero_modbus_bridge.writer import ModbusWriteError, ModbusWriter

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
        writer: ModbusWriter | None = None,
    ):
        """``writer`` executes commands; it may share the reader's client, as all
        Modbus I/O runs on one thread.

        ``buffer_size`` bounds the in-memory queue of readings whose publish
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
        self._writer = writer
        # pyModbusTCP isn't thread-safe, so reads and writes share one thread.
        # Its queue is FIFO and a probe queues one topic at a time, so a
        # command waits for at most one topic read.
        self._modbus_thread = ThreadPoolExecutor(1, thread_name_prefix="modbus")
        self._publisher = publisher
        if probe_interval <= 0:
            raise ValueError("probe_interval must be > 0")
        self._probe_interval = probe_interval
        self._last_read_at: float | None = None

    def has_read_recently(self) -> bool:
        """Whether a probe read at least one topic in the last three probe intervals."""
        return (
            self._last_read_at is not None
            and time.monotonic() - self._last_read_at <= 3 * self._probe_interval
        )

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
        client = modbus_settings.modbus_client()
        publisher = MqttPublisher(broker, topics)
        return ModbusBridge(
            ModbusReader(client, topics),
            publisher,
            topics,
            modbus_settings.modbus_probe_interval,
            buffer_size=buffer_size,
            writer=ModbusWriter(client),
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
        client = ModbusClient(host, port, **client_kwargs)
        return cls(
            ModbusReader(client, topics),
            publisher,
            topics,
            probe_interval,
            buffer_size=buffer_size,
            writer=ModbusWriter(client),
        )

    async def _on_modbus_thread[R](self, call: Callable[..., R], *args: object) -> R:
        return await asyncio.get_running_loop().run_in_executor(
            self._modbus_thread, call, *args
        )

    async def write(self, command: ModbusCommand, message: BaseModel) -> None:
        """Write a validated command message to its unit.

        A failed write is logged, not retried: the sender sees the state that
        took effect on the read topics and sends again if needed.
        """
        if self._writer is None:
            raise RuntimeError("This bridge has no writer for commands")
        writes = command.to_writes(message)
        try:
            await self._on_modbus_thread(self._writer.write, command.unit_id, writes)
        except ModbusWriteError as exc:
            logger.error("Command on %s not applied: %s", command.topic, exc)

    async def run(self) -> None:
        loop = asyncio.get_running_loop()
        next_probe_at = loop.time()
        try:
            while True:
                await self.run_once()
                next_probe_at += self._probe_interval
                await asyncio.sleep(max(0.0, next_probe_at - loop.time()))
        finally:
            # Drop queued reads and writes; only a call already running can
            # still hold up exit, for at most the Modbus timeout.
            self._modbus_thread.shutdown(wait=False, cancel_futures=True)

    async def run_once(self) -> None:
        readings = await self._probe()
        if readings:
            self._last_read_at = time.monotonic()
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

    async def _probe(self) -> list[_Reading] | None:
        """Run the blocking Modbus probe; ``None`` means the gateway is down.

        Each topic is read in its own call on the Modbus thread, so commands
        queued meanwhile go between two topics, and the loop stays responsive
        to MQTT keepalives. Each reading is stamped right after its registers
        were read.

        ``read_all()`` reopens per topic, so the up-front ``ensure_open`` only
        tells a dead gateway (skip the probe) from a mid-cycle drop (skip the
        rest); it doesn't re-dial a live socket.
        """
        if not await self._on_modbus_thread(self._reader.ensure_open):
            return None
        topic_readings = iter(self._reader.read_all())

        def next_reading() -> tuple[str, Any] | None:
            return next(topic_readings, None)

        readings: list[_Reading] = []
        while reading := await self._on_modbus_thread(next_reading):
            topic_name, payload = reading
            readings.append((topic_name, payload, datetime.now(UTC)))
        return readings
