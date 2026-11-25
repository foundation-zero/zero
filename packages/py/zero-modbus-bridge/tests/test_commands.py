from unittest.mock import AsyncMock

import pytest
from faststream.mqtt import MQTTBroker, TestMQTTBroker
from pydantic import BaseModel, Field, ValidationError

from zero_modbus_bridge.commands import ModbusCommand, register_commands


class _SetpointCommand(BaseModel):
    setpoint: float = Field(ge=6, le=70)


_COMMAND = ModbusCommand(
    topic="test/heater/set",
    model=_SetpointCommand,
    unit_id=35,
    to_writes=lambda message: [(12, round(message.setpoint * 100))],
)


@pytest.mark.asyncio
async def test_valid_message_is_written():
    broker = MQTTBroker("localhost:1883")
    write = AsyncMock()
    register_commands(broker, [_COMMAND], write)

    async with TestMQTTBroker(broker) as test_broker:
        await test_broker.publish({"setpoint": 45}, "test/heater/set")

    write.assert_awaited_once_with(_COMMAND, _SetpointCommand(setpoint=45))


@pytest.mark.asyncio
async def test_invalid_message_is_not_written():
    broker = MQTTBroker("localhost:1883")
    write = AsyncMock()
    register_commands(broker, [_COMMAND], write)

    async with TestMQTTBroker(broker) as test_broker:
        with pytest.raises(ValidationError):
            await test_broker.publish({"setpoint": 95}, "test/heater/set")

    write.assert_not_awaited()


def test_to_writes_maps_message_to_registers():
    assert _COMMAND.to_writes(_SetpointCommand(setpoint=45.5)) == [(12, 4550)]
