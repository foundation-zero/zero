from unittest.mock import AsyncMock, MagicMock

import pytest
from zmqtt import MQTTConnectError, MQTTDisconnectedError

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
    await pub.publish("test/p", FloatModel(value=1))
    mock_pub.publish.assert_called_once_with(FloatModel(value=1))


@pytest.mark.asyncio
async def test_publisher_unknown_topic_noop():
    mock_broker = MagicMock()
    pub = MqttPublisher(mock_broker, [])
    await pub.publish("unknown", FloatModel(value=1))


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
    )
    await bridge.run_once()

    mock_modbus.open.assert_called_once()
    mock_pub.publish.assert_called_once()
    payload = mock_pub.publish.call_args.args[0]
    assert payload == FloatModel(value=50.0)


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
    )
    await bridge.run_once()

    mock_modbus.read_holding_registers.assert_not_called()
    mock_pub.publish.assert_not_called()


async def _bridge_from_settings(broker: MagicMock) -> ModbusBridge:
    settings = ModbusSettings(modbus_host="127.0.0.1", modbus_port=1502)
    topic = AnnotationModbusTopic(topic="test/r", model=FloatModel)
    return ModbusBridge.from_settings(settings, broker, [topic])


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

    bridge = ModbusBridge(mock_modbus, mock_broker, [topic], probe_interval=1.0)
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


@pytest.mark.asyncio
async def test_run_once_drops_broker_failure_when_enabled():
    """``drop_failed_publishes`` swallows a broker outage so the loop lives."""
    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock(side_effect=MQTTDisconnectedError("broker gone"))
    bridge = ModbusBridge(
        _reader_yielding("test/t", FloatModel(value=1)),
        mock_pub,
        [],
        drop_failed_publishes=True,
    )

    await bridge.run_once()  # must not raise

    mock_pub.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_once_propagates_broker_failure_by_default():
    """Without the flag a broker outage propagates (historical behaviour)."""
    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock(side_effect=MQTTDisconnectedError("broker gone"))
    bridge = ModbusBridge(_reader_yielding("test/t", FloatModel(value=1)), mock_pub, [])

    with pytest.raises(MQTTDisconnectedError, match="broker gone"):
        await bridge.run_once()

    mock_pub.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_once_propagates_non_broker_error_even_when_dropping():
    """Only broker outages are ridden out; a genuine bug still surfaces."""
    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock(side_effect=ValueError("bug"))
    bridge = ModbusBridge(
        _reader_yielding("test/t", FloatModel(value=1)),
        mock_pub,
        [],
        drop_failed_publishes=True,
    )

    with pytest.raises(ValueError, match="bug"):
        await bridge.run_once()


@pytest.mark.asyncio
async def test_run_once_propagates_persistent_mqtt_error_even_when_dropping():
    """A persistent MQTT misconfig (auth/protocol) surfaces, not just crashes;
    only transient connectivity errors are dropped."""
    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock(side_effect=MQTTConnectError(return_code=5))
    bridge = ModbusBridge(
        _reader_yielding("test/t", FloatModel(value=1)),
        mock_pub,
        [],
        drop_failed_publishes=True,
    )

    with pytest.raises(MQTTConnectError):
        await bridge.run_once()


def test_from_address_applies_modbus_timeout(monkeypatch):
    """A sub-second cadence caps each read so a stalled gateway can't overrun."""
    captured: dict = {}

    def fake_client(host, port, **kwargs):
        captured.update(host=host, port=port, kwargs=kwargs)
        return MagicMock()

    monkeypatch.setattr("zero_modbus_bridge.bridge.ModbusClient", fake_client)
    ModbusBridge.from_address("10.0.0.1", 502, MagicMock(), [], modbus_timeout=0.5)

    assert captured["kwargs"]["timeout"] == 0.5


def test_from_address_omits_timeout_by_default(monkeypatch):
    """Without an explicit timeout we leave pyModbusTCP's own default in place."""
    captured: dict = {}

    def fake_client(host, port, **kwargs):
        captured.update(kwargs=kwargs)
        return MagicMock()

    monkeypatch.setattr("zero_modbus_bridge.bridge.ModbusClient", fake_client)
    ModbusBridge.from_address("10.0.0.1", 502, MagicMock(), [])

    assert "timeout" not in captured["kwargs"]


def test_from_address_accepts_timeout_on_real_client():
    """The real ModbusClient accepts the timeout kwarg (no mock, no I/O)."""
    bridge = ModbusBridge.from_address(
        "10.0.0.1", 502, MagicMock(), [], modbus_timeout=0.5
    )
    assert isinstance(bridge, ModbusBridge)
