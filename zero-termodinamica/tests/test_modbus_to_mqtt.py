import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from zero_termodinamica.io import Address, LiteralField, ModbusUnit, MqttTopic
from zero_termodinamica.modbus_to_mqtt import ModbusToMQTTBridge


@pytest.mark.asyncio
async def test_run_once_success():
    # Mock ModbusClient
    mock_modbus = MagicMock()
    # Mock MqttClient
    mock_mqtt = AsyncMock()

    # Simple address for testing
    modbus_units = [
        ModbusUnit(
            unit_id=1,
            topics=[
                MqttTopic(
                    topic="test/topic",
                    modbus_fields=[
                        Address(
                            modbus_register=200,
                            field_name="PWR",
                            scale_factor=1.0,
                        )
                    ],
                )
            ],
        )
    ]

    bridge = ModbusToMQTTBridge(mock_modbus, mock_mqtt, modbus_units)

    # Setup mock returns: Modbus returns 1 for the register
    mock_modbus.read_holding_registers.return_value = [1]

    await bridge.run_once()

    # Check if mqtt publish was called with correct data
    mock_mqtt.publish.assert_called_once_with("test/topic", '{"PWR": 1.0}', qos=1)


@pytest.mark.asyncio
async def test_run_once_multiple_addresses_scaling():
    # Mock ModbusClient
    mock_modbus = MagicMock()
    # Mock MqttClient
    mock_mqtt = AsyncMock()

    # Two addresses on the same topic with different scaling
    modbus_units = [
        ModbusUnit(
            unit_id=1,
            topics=[
                MqttTopic(
                    topic="test/topic",
                    modbus_fields=[
                        Address(
                            modbus_register=200,
                            field_name="PWR",
                            scale_factor=1.0,
                        ),
                        Address(
                            modbus_register=201,
                            field_name="TEMP",
                            scale_factor=0.1,
                        ),
                    ],
                )
            ],
        )
    ]

    bridge = ModbusToMQTTBridge(mock_modbus, mock_mqtt, modbus_units)

    # Setup mock returns
    def read_side_effect(modbus_register, count):
        if modbus_register == 200:
            return [1]
        if modbus_register == 201:
            return [235]
        return None

    mock_modbus.read_holding_registers.side_effect = read_side_effect

    await bridge.run_once()

    # Check if mqtt publish was called once (since same topic) with correct JSON
    # Note: groupby preserves order, so we expect both in one JSON if they are contiguous
    args, kwargs = mock_mqtt.publish.call_args
    assert args[0] == "test/topic"
    data = json.loads(args[1])
    assert data == {"PWR": 1.0, "TEMP": 23.5}
    assert kwargs["qos"] == 1


@pytest.mark.asyncio
async def test_run_once_multiple_topics():
    # Mock ModbusClient
    mock_modbus = MagicMock()
    # Mock MqttClient
    mock_mqtt = AsyncMock()

    modbus_units = [
        ModbusUnit(
            unit_id=1,
            topics=[
                MqttTopic(
                    topic="topic/1",
                    modbus_fields=[
                        Address(modbus_register=200, field_name="VAL1"),
                    ],
                ),
                MqttTopic(
                    topic="topic/2",
                    modbus_fields=[
                        Address(modbus_register=300, field_name="VAL2"),
                    ],
                ),
            ],
        )
    ]
    bridge = ModbusToMQTTBridge(mock_modbus, mock_mqtt, modbus_units)

    def read_side_effect(modbus_register, count):
        if modbus_register == 200:
            return [10]
        if modbus_register == 300:
            return [20]
        return None

    mock_modbus.read_holding_registers.side_effect = read_side_effect

    await bridge.run_once()

    assert mock_mqtt.publish.call_count == 2

    # Check first call
    call1 = mock_mqtt.publish.call_args_list[0]
    assert call1.args[0] == "topic/1"
    assert json.loads(call1.args[1]) == {"VAL1": 10.0}

    # Check second call
    call2 = mock_mqtt.publish.call_args_list[1]
    assert call2.args[0] == "topic/2"
    assert json.loads(call2.args[1]) == {"VAL2": 20.0}


@pytest.mark.asyncio
async def test_run_once_with_literal_fields():
    # Mock ModbusClient
    mock_modbus = MagicMock()
    # Mock MqttClient
    mock_mqtt = AsyncMock()

    modbus_units = [
        ModbusUnit(
            unit_id=1,
            topics=[
                MqttTopic(
                    topic="test/topic",
                    modbus_fields=[
                        Address(
                            modbus_register=200,
                            field_name="PWR",
                            scale_factor=1.0,
                        )
                    ],
                    extra_fields=[
                        LiteralField(field_name="room", value="Galley"),
                        LiteralField(field_name="reg_split", value=18),
                    ],
                )
            ],
        )
    ]

    bridge = ModbusToMQTTBridge(mock_modbus, mock_mqtt, modbus_units)

    # Setup mock return: Modbus returns 1
    mock_modbus.read_holding_registers.return_value = [1]

    await bridge.run_once()

    # Check if mqtt publish was called with correct data including literal fields
    args, kwargs = mock_mqtt.publish.call_args
    assert args[0] == "test/topic"
    data = json.loads(args[1])
    assert data == {"room": "Galley", "reg_split": 18, "PWR": 1.0}
    assert kwargs["qos"] == 1


@pytest.mark.asyncio
async def test_run_multiple_cycles():
    # Mock ModbusClient
    mock_modbus = MagicMock()
    # Mock MqttClient
    mock_mqtt = AsyncMock()

    # Simple address for testing
    modbus_units = [
        ModbusUnit(
            unit_id=1,
            topics=[
                MqttTopic(
                    topic="test/topic",
                    modbus_fields=[
                        Address(modbus_register=200, field_name="PWR", scale_factor=1.0)
                    ],
                )
            ],
        )
    ]

    # probe_interval=0.5s, run for 1s -> expect exactly 2 cycles
    bridge = ModbusToMQTTBridge(
        mock_modbus, mock_mqtt, modbus_units, probe_interval=0.5
    )

    # Setup mock returns: Modbus returns 1 for the register
    mock_modbus.read_holding_registers.return_value = [1]

    # Run the bridge for ~1 second
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(bridge.run(), timeout=1)

    # Verify exactly 2 cycles occurred
    assert mock_mqtt.publish.call_count == 2

    # Verify each call has correct format
    for call in mock_mqtt.publish.call_args_list:
        assert call.args[0] == "test/topic"
        data = json.loads(call.args[1])
        assert data == {"PWR": 1.0}
        assert call.kwargs["qos"] == 1
