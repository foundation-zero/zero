from typing import Annotated
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel
from zero_modbus_bridge.bridge import ModbusBridge
from zero_modbus_bridge.io import ModbusField, ModbusTopic


def _make_bridge(mock_modbus, topics):
    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock()
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = mock_pub
    return ModbusBridge(mock_modbus, mock_broker, topics), mock_pub


class _PwrModel(BaseModel):
    power: Annotated[float | None, ModbusField(register=10, scale_factor=1.0)]


class _TempModel(BaseModel):
    power: Annotated[float | None, ModbusField(register=10, scale_factor=0.04)]
    temperature: Annotated[float | None, ModbusField(register=11, scale_factor=0.01)]


class _ValueModel(BaseModel):
    model_config = {"extra": "allow"}
    value: Annotated[int | None, ModbusField(register=1)]


class _Value2Model(BaseModel):
    value2: Annotated[int | None, ModbusField(register=2)]


@pytest.mark.asyncio
async def test_run_once_success():
    mock_modbus = MagicMock(host="127.0.0.1", port=502, is_open=False)
    mock_modbus.open.return_value = True
    mock_modbus.read_holding_registers.return_value = [1]

    topics = [ModbusTopic(topic="test/pwr", model=_PwrModel)]
    bridge, mock_pub = _make_bridge(mock_modbus, topics)
    await bridge.run_once()
    mock_pub.publish.assert_called_once_with(_PwrModel(power=1.0))


@pytest.mark.asyncio
async def test_run_once_multiple_addresses_scaling():
    mock_modbus = MagicMock(host="127.0.0.1", port=502, is_open=False)
    mock_modbus.open.return_value = True
    mock_modbus.read_holding_registers.side_effect = [[25], [100]]

    topics = [ModbusTopic(topic="test/temp", model=_TempModel)]
    bridge, mock_pub = _make_bridge(mock_modbus, topics)
    await bridge.run_once()
    mock_pub.publish.assert_called_once()
    payload = mock_pub.publish.call_args.args[0]
    assert payload.power == 1.0
    assert payload.temperature == 1.0


@pytest.mark.asyncio
async def test_run_once_multiple_topics():
    mock_modbus = MagicMock(host="127.0.0.1", port=502, is_open=False)
    mock_modbus.open.return_value = True
    mock_modbus.read_holding_registers.return_value = [10]

    mock_pub1 = MagicMock()
    mock_pub1.publish = AsyncMock()
    mock_pub2 = MagicMock()
    mock_pub2.publish = AsyncMock()
    mock_broker = MagicMock()
    mock_broker.publisher.side_effect = [mock_pub1, mock_pub2]

    topics = [
        ModbusTopic(topic="test/val", model=_ValueModel),
        ModbusTopic(topic="test/val2", model=_Value2Model),
    ]
    bridge = ModbusBridge(mock_modbus, mock_broker, topics)
    await bridge.run_once()
    mock_pub1.publish.assert_called_once_with(_ValueModel(value=10))
    mock_pub2.publish.assert_called_once_with(_Value2Model(value2=10))


@pytest.mark.asyncio
async def test_run_once_with_extra_fields():
    mock_modbus = MagicMock(host="127.0.0.1", port=502, is_open=False)
    mock_modbus.open.return_value = True
    mock_modbus.read_holding_registers.return_value = [5]

    topics = [
        ModbusTopic(
            topic="test/extra",
            model=_ValueModel,
            extra_fields={"location": "deck1"},
        )
    ]
    bridge, mock_pub = _make_bridge(mock_modbus, topics)
    await bridge.run_once()
    mock_pub.publish.assert_called_once()
    payload = mock_pub.publish.call_args.args[0]
    assert payload.value == 5
    assert payload.location == "deck1"


@pytest.mark.asyncio
async def test_run_multiple_cycles():
    import asyncio

    mock_modbus = MagicMock(host="127.0.0.1", port=502, is_open=False)
    mock_modbus.open.return_value = True
    mock_modbus.read_holding_registers.return_value = [1]

    topics = [ModbusTopic(topic="test/pwr", model=_PwrModel)]
    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock()
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = mock_pub

    bridge = ModbusBridge(mock_modbus, mock_broker, topics, probe_interval=0.01)
    task = asyncio.ensure_future(bridge.run())
    await asyncio.sleep(0.05)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    assert mock_pub.publish.call_count >= 2
