from collections import Counter
from unittest.mock import MagicMock

import pytest
from zero_modbus_bridge.io import extract_modbus_fields
from zero_modbus_bridge.reader import ModbusReader

from zero_termodinamica.io import (
    ColdRoom,
    HeatPump,
    VentilationUnit,
    read_modbus_topics,
)


def test_io():
    topics = read_modbus_topics()
    # AC: the 30 units on the wiring schematic and ac-misc. Ventilation: the
    # populated slots of each bridge. Heat pump, fridge and freezer: one each.
    assert Counter(t.unit_id for t in topics) == {
        32: 31,
        33: 13,
        34: 8,
        35: 1,
        36: 1,
        37: 1,
    }


def test_ventilation_topics_follow_dvs_register_map():
    ventilation = [
        t
        for t in read_modbus_topics()
        if t.topic.startswith("termodinamica/ventilation/")
    ]

    assert {t.unit_id for t in ventilation} == {33, 34}
    unit_5 = next(
        t for t in ventilation if t.topic == "termodinamica/ventilation/day-head"
    )
    assert unit_5.model is VentilationUnit
    assert unit_5.start_register == 130
    assert unit_5.extra_fields == {"bridge": "2", "unit": "05", "room": "Day head"}


def test_heat_pump_topic_reads_control_registers():
    heat_pump = next(
        t for t in read_modbus_topics() if t.topic == "termodinamica/heat-pump"
    )

    assert heat_pump.unit_id == 35
    assert heat_pump.model is HeatPump
    fields = extract_modbus_fields(HeatPump)
    assert fields["system_disabled"].register == 30
    assert fields["compressor_speed"].register == 140
    assert heat_pump.start_register == 210
    assert fields["setpoint_temperature"].offset == 1


def test_cold_rooms_read_signed_temperatures():
    cold_rooms = {t.topic: t for t in read_modbus_topics() if t.model is ColdRoom}

    assert {name: t.unit_id for name, t in cold_rooms.items()} == {
        "termodinamica/fridge": 36,
        "termodinamica/freezer": 37,
    }
    freezer = cold_rooms["termodinamica/freezer"]
    # Live freezer values: slot 3, -18.00 °C set point, -12.53 °C
    registers = {221: 63736, 223: 64283}
    modbus = MagicMock()
    modbus.read_holding_registers.side_effect = lambda register, _: [
        registers.get(register, 0)
    ]

    payload = ModbusReader(modbus, [freezer]).read_topic(freezer)

    assert payload.setpoint_temperature == pytest.approx(-18.0)
    assert payload.temperature == pytest.approx(-12.53)
    assert cold_rooms["termodinamica/fridge"].start_register == 210


def test_ac_room_temperatures_are_in_degrees_celsius():
    room = next(
        t for t in read_modbus_topics() if t.topic == "termodinamica/ac/tech-room"
    )
    # Live room 01: set point 22.00 °C, 18.90 °C
    registers = {201: 2200, 203: 1890}
    modbus = MagicMock()
    modbus.read_holding_registers.side_effect = lambda register, _: [
        registers.get(register, 0)
    ]

    payload = ModbusReader(modbus, [room]).read_topic(room)

    assert payload.setpoint_room_temperature == 22.0
    assert payload.air_temperature_in == 18.9
    assert payload.room == "Tech room"


def test_ventilation_payload_names_its_room():
    unit = next(
        t
        for t in read_modbus_topics()
        if t.topic == "termodinamica/ventilation/lower-salon"
    )

    payload = ModbusReader(
        MagicMock(**{"read_holding_registers.return_value": [0]}), [unit]
    ).read_topic(unit)

    assert (payload.bridge, payload.unit, payload.room) == ("2", "03", "Lower salon")
