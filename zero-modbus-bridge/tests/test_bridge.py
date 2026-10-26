from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel
from zmqtt import (
    MQTTConnectError,
    MQTTDisconnectedError,
    MQTTPublishError,
    MQTTTimeoutError,
)

from tests.conftest import FloatModel
from zero_modbus_bridge.bridge import ModbusBridge
from zero_modbus_bridge.io import AnnotationModbusTopic
from zero_modbus_bridge.publisher import MqttPublisher
from zero_modbus_bridge.reader import ModbusReader
from zero_modbus_bridge.settings import ModbusSettings


@pytest.mark.asyncio
async def test_publisher_registers_and_publishes():
    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock()
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = mock_pub

    topic = AnnotationModbusTopic(topic="test/p", model=FloatModel)
    pub = MqttPublisher(mock_broker, [topic])
    read_at = datetime(2026, 10, 13, 9, 30, tzinfo=UTC)
    await pub.publish("test/p", FloatModel(value=1), read_at)
    mock_pub.publish.assert_called_once_with(
        {"value": 1.0, "room": None, "TimeStamp": "2026-10-13T09:30:00Z"}
    )


@pytest.mark.asyncio
async def test_publisher_unknown_topic_noop():
    mock_broker = MagicMock()
    pub = MqttPublisher(mock_broker, [])
    await pub.publish("unknown", FloatModel(value=1), datetime.now(UTC))


@pytest.mark.asyncio
async def test_bridge_run_once_annotation():
    mock_modbus = MagicMock(host="127.0.0.1", port=502, is_open=False)

    def _open() -> bool:
        mock_modbus.is_open = True
        return True

    mock_modbus.open.side_effect = _open
    mock_modbus.read_holding_registers.return_value = [0x4248, 0x0000]

    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock()
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = mock_pub

    topic = AnnotationModbusTopic(
        topic="test/b",
        model=FloatModel,
        start_register=3000,
    )
    bridge = ModbusBridge(
        ModbusReader(mock_modbus, [topic]),
        MqttPublisher(mock_broker, [topic]),
        [topic],
        buffer_size=10,
    )
    before = datetime.now(UTC)
    await bridge.run_once()
    after = datetime.now(UTC)

    mock_modbus.open.assert_called_once()
    mock_pub.publish.assert_called_once()
    body = mock_pub.publish.call_args.args[0]
    read_at = datetime.fromisoformat(body.pop("TimeStamp"))
    assert before <= read_at <= after
    assert body == {"value": 50.0, "room": None}


@pytest.mark.asyncio
async def test_bridge_run_once_skips_probe_when_connection_unavailable():
    mock_modbus = MagicMock(host="127.0.0.1", port=502, is_open=False)
    mock_modbus.open.return_value = False

    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock()
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = mock_pub

    topic = AnnotationModbusTopic(topic="test/skip", model=FloatModel)
    bridge = ModbusBridge(
        ModbusReader(mock_modbus, [topic]),
        MqttPublisher(mock_broker, [topic]),
        [topic],
        buffer_size=10,
    )
    await bridge.run_once()

    mock_modbus.read_holding_registers.assert_not_called()
    mock_pub.publish.assert_not_called()


async def _bridge_from_settings(broker: MagicMock) -> ModbusBridge:
    settings = ModbusSettings(modbus_host="127.0.0.1", modbus_port=1502)
    topic = AnnotationModbusTopic(topic="test/r", model=FloatModel)
    return ModbusBridge.from_settings(settings, broker, [topic], buffer_size=10)


@pytest.mark.asyncio
async def test_bridge_initialization_registers_publishers():
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = MagicMock()

    await _bridge_from_settings(mock_broker)
    mock_broker.publisher.assert_called_once()


@pytest.mark.asyncio
async def test_bridge_run_calls_run_once_before_sleep(monkeypatch):
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = MagicMock()
    topic = AnnotationModbusTopic(topic="test/r", model=FloatModel)

    bridge = ModbusBridge(
        ModbusReader(MagicMock(is_open=True), [topic]),
        MqttPublisher(mock_broker, [topic]),
        [topic],
        probe_interval=10,
        buffer_size=10,
    )
    bridge.run_once = AsyncMock(side_effect=RuntimeError("stop"))
    sleep_mock = AsyncMock()
    monkeypatch.setattr("zero_modbus_bridge.bridge.asyncio.sleep", sleep_mock)

    with pytest.raises(RuntimeError, match="stop"):
        await bridge.run()

    bridge.run_once.assert_awaited_once()
    sleep_mock.assert_not_called()


@pytest.mark.asyncio
async def test_bridge_run_compensates_for_run_once_duration(monkeypatch):
    mock_modbus = MagicMock(host="127.0.0.1", port=502, is_open=True)
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = MagicMock()
    topic = AnnotationModbusTopic(topic="test/r", model=FloatModel)

    bridge = ModbusBridge(
        mock_modbus, mock_broker, [topic], probe_interval=1.0, buffer_size=10
    )
    bridge.run_once = AsyncMock(side_effect=[None, RuntimeError("stop")])
    sleep_mock = AsyncMock()
    loop_mock = MagicMock()
    loop_mock.time = MagicMock(side_effect=[100.0, 100.4])

    monkeypatch.setattr("zero_modbus_bridge.bridge.asyncio.sleep", sleep_mock)
    monkeypatch.setattr(
        "zero_modbus_bridge.bridge.asyncio.get_running_loop", lambda: loop_mock
    )

    with pytest.raises(RuntimeError, match="stop"):
        await bridge.run()

    assert sleep_mock.await_count == 1
    await_args = sleep_mock.await_args
    assert await_args is not None
    assert await_args.args[0] == pytest.approx(0.6)


def _reader_yielding(topic: str, payload) -> MagicMock:
    reader = MagicMock()
    reader.ensure_open.return_value = True
    reader.read_all.return_value = [(topic, payload)]
    return reader


class RecordingPublisher:
    """Publisher whose broker can be switched between refusing and accepting."""

    def __init__(self) -> None:
        self.error: Exception | None = None
        self.accepted: list[tuple[str, BaseModel, datetime]] = []

    async def publish(self, topic: str, payload: BaseModel, read_at: datetime) -> None:
        if self.error is not None:
            raise self.error
        self.accepted.append((topic, payload, read_at))


def _bridge(
    publisher: RecordingPublisher, *, buffer_size: int = 10
) -> tuple[ModbusBridge, MagicMock]:
    reader = MagicMock()
    reader.ensure_open.return_value = True
    reader.read_all.return_value = []
    return ModbusBridge(reader, publisher, [], buffer_size=buffer_size), reader


def _probe_yields(reader: MagicMock, *values: float) -> None:
    reader.read_all.return_value = [("test/t", FloatModel(value=v)) for v in values]


@pytest.mark.parametrize(
    "error",
    [
        MQTTPublishError(0x83, "Implementation specific error", None),
        MQTTDisconnectedError("broker gone"),
        MQTTTimeoutError("no ack"),
    ],
)
@pytest.mark.asyncio
async def test_failed_publish_is_buffered_and_replayed_in_order(error: Exception):
    publisher = RecordingPublisher()
    bridge, reader = _bridge(publisher)

    publisher.error = error
    _probe_yields(reader, 1)
    await bridge.run_once()
    _probe_yields(reader, 2)
    await bridge.run_once()
    _probe_yields(reader, 3)
    await bridge.run_once()

    assert publisher.accepted == []
    assert bridge.buffered_count == 3

    publisher.error = None
    _probe_yields(reader, 4)
    await bridge.run_once()

    assert [payload.value for _, payload, _ in publisher.accepted] == [1, 2, 3, 4]  # type: ignore[attr-defined]
    assert bridge.buffered_count == 0
    assert bridge.dropped_count == 0


@pytest.mark.asyncio
async def test_partial_flush_keeps_order_and_never_resends():
    class FailsAfterTwo(RecordingPublisher):
        async def publish(
            self, topic: str, payload: BaseModel, read_at: datetime
        ) -> None:
            if len(self.accepted) == 2 and self.error is not None:
                raise self.error
            self.accepted.append((topic, payload, read_at))

    publisher = FailsAfterTwo()
    bridge, reader = _bridge(publisher)
    publisher.error = MQTTPublishError(0x83, "Implementation specific error", None)

    _probe_yields(reader, 1, 2, 3, 4)
    await bridge.run_once()

    assert [p.value for _, p, _ in publisher.accepted] == [1, 2]  # type: ignore[attr-defined]
    assert bridge.buffered_count == 2

    publisher.error = None
    _probe_yields(reader, 5)
    await bridge.run_once()

    assert [p.value for _, p, _ in publisher.accepted] == [1, 2, 3, 4, 5]  # type: ignore[attr-defined]
    assert bridge.buffered_count == 0


@pytest.mark.asyncio
async def test_replay_keeps_the_original_read_time():
    publisher = RecordingPublisher()
    bridge, reader = _bridge(publisher)

    publisher.error = MQTTPublishError(0x83, "Implementation specific error", None)
    _probe_yields(reader, 1)
    before = datetime.now(UTC)
    await bridge.run_once()
    after = datetime.now(UTC)

    publisher.error = None
    _probe_yields(reader)
    await bridge.run_once()

    ((_, _, read_at),) = publisher.accepted
    assert before <= read_at <= after
    assert read_at.tzinfo is not None


@pytest.mark.asyncio
async def test_oldest_dropped_when_buffer_is_full():
    publisher = RecordingPublisher()
    bridge, reader = _bridge(publisher, buffer_size=3)

    publisher.error = MQTTDisconnectedError("broker gone")
    for value in range(1, 6):
        _probe_yields(reader, value)
        await bridge.run_once()

    assert bridge.buffered_count == 3
    assert bridge.dropped_count == 2

    publisher.error = None
    _probe_yields(reader)
    await bridge.run_once()

    assert [payload.value for _, payload, _ in publisher.accepted] == [3, 4, 5]  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_recovery_probe_does_not_push_out_a_full_backlog():
    publisher = RecordingPublisher()
    bridge, reader = _bridge(publisher, buffer_size=3)

    publisher.error = MQTTDisconnectedError("broker gone")
    for value in range(1, 4):
        _probe_yields(reader, value)
        await bridge.run_once()

    publisher.error = None
    _probe_yields(reader, 4)
    await bridge.run_once()

    assert [payload.value for _, payload, _ in publisher.accepted] == [1, 2, 3, 4]  # type: ignore[attr-defined]
    assert bridge.dropped_count == 0


@pytest.mark.asyncio
async def test_bridge_keeps_running_through_a_long_outage():
    publisher = RecordingPublisher()
    bridge, reader = _bridge(publisher, buffer_size=2)
    publisher.error = MQTTPublishError(0x83, "Implementation specific error", None)

    for value in range(50):
        _probe_yields(reader, value)
        await bridge.run_once()

    assert bridge.buffered_count == 2


@pytest.mark.asyncio
async def test_buffer_is_flushed_while_the_gateway_is_down():
    publisher = RecordingPublisher()
    bridge, reader = _bridge(publisher)

    publisher.error = MQTTPublishError(0x83, "Implementation specific error", None)
    _probe_yields(reader, 1)
    await bridge.run_once()

    publisher.error = None
    reader.ensure_open.return_value = False
    await bridge.run_once()

    assert bridge.buffered_count == 0
    assert len(publisher.accepted) == 1


@pytest.mark.asyncio
async def test_non_broker_error_still_propagates():
    publisher = RecordingPublisher()
    bridge, reader = _bridge(publisher)
    publisher.error = ValueError("bug")
    _probe_yields(reader, 1)

    with pytest.raises(ValueError, match="bug"):
        await bridge.run_once()


@pytest.mark.asyncio
async def test_persistent_mqtt_error_still_propagates():
    """A persistent MQTT misconfig (auth/protocol) surfaces instead of buffering."""
    publisher = RecordingPublisher()
    bridge, reader = _bridge(publisher)
    publisher.error = MQTTConnectError(return_code=5)
    _probe_yields(reader, 1)

    with pytest.raises(MQTTConnectError):
        await bridge.run_once()


@pytest.mark.parametrize("size", [0, -1])
def test_buffer_size_must_be_positive(size: int):
    with pytest.raises(ValueError, match="buffer_size"):
        _bridge(RecordingPublisher(), buffer_size=size)


def test_from_address_applies_modbus_timeout(monkeypatch):
    """A sub-second cadence caps each read so a stalled gateway can't overrun."""
    captured: dict = {}

    def fake_client(host, port, **kwargs):
        captured.update(host=host, port=port, kwargs=kwargs)
        return MagicMock()

    monkeypatch.setattr("zero_modbus_bridge.bridge.ModbusClient", fake_client)
    ModbusBridge.from_address(
        "10.0.0.1", 502, MagicMock(), [], modbus_timeout=0.5, buffer_size=10
    )

    assert captured["kwargs"]["timeout"] == 0.5


def test_from_address_omits_timeout_by_default(monkeypatch):
    """Without an explicit timeout we leave pyModbusTCP's own default in place."""
    captured: dict = {}

    def fake_client(host, port, **kwargs):
        captured.update(kwargs=kwargs)
        return MagicMock()

    monkeypatch.setattr("zero_modbus_bridge.bridge.ModbusClient", fake_client)
    ModbusBridge.from_address("10.0.0.1", 502, MagicMock(), [], buffer_size=10)

    assert "timeout" not in captured["kwargs"]


def test_from_address_accepts_timeout_on_real_client():
    """The real ModbusClient accepts the timeout kwarg (no mock, no I/O)."""
    bridge = ModbusBridge.from_address(
        "10.0.0.1", 502, MagicMock(), [], modbus_timeout=0.5, buffer_size=10
    )
    assert isinstance(bridge, ModbusBridge)
