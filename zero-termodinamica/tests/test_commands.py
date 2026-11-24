from unittest.mock import AsyncMock

import pytest
from faststream.mqtt import MQTTBroker, TestMQTTBroker
from pydantic import ValidationError
from zero_modbus_bridge.commands import register_commands

from zero_termodinamica.commands import HeatPumpSet, heat_pump_writes, modbus_commands
from zero_termodinamica.io import read_modbus_topics


def test_switching_on_enables_the_system_before_the_unit():
    writes = heat_pump_writes(HeatPumpSet(power=True, setpoint_temperature=45))

    assert writes == [(30, 0), (11, 1), (12, 4500), (10, 2)]


def test_switching_off_stops_the_unit_before_the_system():
    writes = heat_pump_writes(HeatPumpSet(power=False, setpoint_temperature=45))

    assert writes == [(11, 0), (12, 4500), (10, 2), (30, 1)]


def test_setpoint_is_rounded_to_whole_degrees():
    writes = dict(heat_pump_writes(HeatPumpSet(power=True, setpoint_temperature=44.6)))

    assert writes[12] == 4500


@pytest.mark.parametrize("setpoint", [5.9, 70.1])
def test_setpoint_outside_the_heat_pump_range_is_rejected(setpoint: float):
    with pytest.raises(ValidationError):
        HeatPumpSet(power=True, setpoint_temperature=setpoint)


def test_heat_pump_command_writes_to_the_unit_it_reads():
    (command,) = modbus_commands(read_modbus_topics())

    assert command.topic == "termodinamica/heat-pump/set"
    assert command.unit_id == 35


@pytest.mark.asyncio
async def test_heat_pump_command_topic_reaches_the_bridge():
    commands = modbus_commands(read_modbus_topics())
    broker = MQTTBroker("localhost:1883")
    write = AsyncMock()
    register_commands(broker, commands, write)

    async with TestMQTTBroker(broker) as test_broker:
        await test_broker.publish(
            {"power": True, "setpoint_temperature": 50}, "termodinamica/heat-pump/set"
        )

    write.assert_awaited_once_with(
        commands[0], HeatPumpSet(power=True, setpoint_temperature=50)
    )
