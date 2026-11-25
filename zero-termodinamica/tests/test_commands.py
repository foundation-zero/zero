from unittest.mock import AsyncMock

import pytest
from faststream.mqtt import MQTTBroker, TestMQTTBroker
from pydantic import ValidationError
from zero_modbus_bridge.commands import register_commands

from zero_termodinamica.commands import HeatPumpSet, heat_pump_writes, modbus_commands
from zero_termodinamica.io import read_modbus_topics


@pytest.mark.parametrize("power", [True, False])
def test_unit_batch_goes_before_the_global_switch(power: bool):
    writes = heat_pump_writes(
        HeatPumpSet(power=power, setpoint_temperature=45), slave=2
    )

    assert writes == [(11, int(power)), (12, 4500), (10, 2), (30, 0 if power else 1)]


@pytest.mark.parametrize(
    ("setpoint", "written"), [(44.5, 4500), (45.5, 4600), (44.4, 4400)]
)
def test_setpoint_is_rounded_half_up_to_whole_degrees(setpoint: float, written: int):
    writes = dict(
        heat_pump_writes(
            HeatPumpSet(power=True, setpoint_temperature=setpoint), slave=2
        )
    )

    assert writes[12] == written


@pytest.mark.parametrize("setpoint", [5.9, 70.1])
def test_setpoint_outside_the_heat_pump_range_is_rejected(setpoint: float):
    with pytest.raises(ValidationError):
        HeatPumpSet(power=True, setpoint_temperature=setpoint)


def test_heat_pump_command_writes_to_the_unit_it_reads():
    (command,) = modbus_commands(read_modbus_topics())

    assert command.topic == "termodinamica/heat-pump/set"
    assert command.unit_id == 35
    # The command selects the slave the heat-pump topic reads
    assert (
        dict(command.to_writes(HeatPumpSet(power=True, setpoint_temperature=45)))[10]
        == 2
    )


def test_missing_heat_pump_topic_is_named():
    with pytest.raises(ValueError, match="termodinamica/heat-pump"):
        modbus_commands([])


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
