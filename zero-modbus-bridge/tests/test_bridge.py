from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.conftest import FloatModel
from zero_modbus_bridge.bridge import ModbusBridge
from zero_modbus_bridge.io import ModbusTopic
from zero_modbus_bridge.publisher import MqttPublisher


@pytest.mark.asyncio
async def test_publisher_registers_and_publishes():
    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock()
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = mock_pub

    topic = ModbusTopic(topic="test/p", model=FloatModel)
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
    mock_modbus.open.return_value = True
    mock_modbus.read_holding_registers.return_value = [0x4248, 0x0000]

    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock()
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = mock_pub

    topic = ModbusTopic(
        topic="test/b",
        model=FloatModel,
        start_register=3000,
    )
    bridge = ModbusBridge(mock_modbus, mock_broker, [topic])
    await bridge.run_once()

    mock_pub.publish.assert_called_once()
    payload = mock_pub.publish.call_args.args[0]
    assert payload == FloatModel(value=50.0)


@pytest.mark.asyncio
async def test_bridge_initialization_registers_publishers():
    mock_modbus = MagicMock(host="127.0.0.1", port=502, is_open=False)
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = MagicMock()

    topic = ModbusTopic(topic="test/r", model=FloatModel)
    ModbusBridge(mock_modbus, mock_broker, [topic])
    mock_broker.publisher.assert_called_once()


@pytest.mark.asyncio
async def test_bridge_run_calls_run_once_before_sleep(monkeypatch):
    mock_modbus = MagicMock(host="127.0.0.1", port=502, is_open=True)
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = MagicMock()
    topic = ModbusTopic(topic="test/r", model=FloatModel)

    bridge = ModbusBridge(mock_modbus, mock_broker, [topic], probe_interval=10)
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
    topic = ModbusTopic(topic="test/r", model=FloatModel)

    bridge = ModbusBridge(mock_modbus, mock_broker, [topic], probe_interval=1.0)
    bridge.run_once = AsyncMock(side_effect=[None, RuntimeError("stop")])
    sleep_mock = AsyncMock()
    loop_mock = MagicMock()
    loop_mock.time = MagicMock(side_effect=[100.0, 100.4])

    monkeypatch.setattr("zero_modbus_bridge.bridge.asyncio.sleep", sleep_mock)
    monkeypatch.setattr("zero_modbus_bridge.bridge.asyncio.get_running_loop", lambda: loop_mock)

    with pytest.raises(RuntimeError, match="stop"):
        await bridge.run()

    assert sleep_mock.await_count == 1
    await_args = sleep_mock.await_args
    assert await_args is not None
    assert await_args.args[0] == pytest.approx(0.6)
