import pytest

from zero_modbus_bridge.bit_ops import (
    float_to_lsw_registers,
    int16_to_uint16,
    is_finite_float,
    lsw_registers_to_float,
    to_raw,
    uint16_to_int16,
)
from zero_modbus_bridge.io import ModbusField, apply_modbus_field


def test_lsw_registers_to_float_known_value():
    # Example from hull-temperature docs
    assert lsw_registers_to_float([0x419D, 0xD4E6]) == 19.728954315185547


def test_float_to_lsw_registers_roundtrip():
    assert float_to_lsw_registers(19.728954315185547) == [0x419D, 0xD4E6]


def test_lsw_registers_to_float_50():
    # 50.0f in IEEE 754 big-endian: 0x42480000 → [0x4248, 0x0000]
    assert lsw_registers_to_float([0x4248, 0x0000]) == 50.0


def test_float_to_lsw_registers_50():
    assert float_to_lsw_registers(50.0) == [0x4248, 0x0000]


def test_lsw_registers_to_float_zero():
    assert lsw_registers_to_float([0x0000, 0x0000]) == 0.0


def test_float_to_lsw_registers_zero():
    assert float_to_lsw_registers(0.0) == [0x0000, 0x0000]


def test_is_finite_float_rejects_nan_sentinel():
    # 0xFFC00000 decodes to NaN - the invalid-value sentinel
    sentinel = lsw_registers_to_float([0xFFC0, 0x0000])
    assert is_finite_float(sentinel) is False


def test_is_finite_float_accepts_normal():
    assert is_finite_float(50.0) is True


def test_is_finite_float_rejects_infinity():
    assert is_finite_float(float("inf")) is False
    assert is_finite_float(float("-inf")) is False


def test_uint16_to_int16_reads_twos_complement():
    assert uint16_to_int16(0xFFFF) == -1
    assert uint16_to_int16(0x10000 - 1000) == -1000
    assert uint16_to_int16(0x7FFF) == 0x7FFF
    assert uint16_to_int16(0x8000) == -0x8000


def test_int16_to_uint16_round_trip():
    assert [uint16_to_int16(int16_to_uint16(v)) for v in (-0x8000, -1, 0, 0x7FFF)] == [
        -0x8000,
        -1,
        0,
        0x7FFF,
    ]


@pytest.mark.parametrize(
    ("value", "field", "raw"),
    [
        (45.0, ModbusField(register=1, scale_factor=0.01), 4500),
        (-18.0, ModbusField(register=1, data_type="int16", scale_factor=0.01), 63736),
        (1, ModbusField(register=1), 1),
    ],
)
def test_to_raw_is_the_inverse_of_reading(value, field, raw):
    assert to_raw(value, field) == raw
    assert (
        apply_modbus_field(
            uint16_to_int16(raw) if field.data_type == "int16" else raw, field
        )
        == value
    )


@pytest.mark.parametrize(
    ("value", "field"),
    [
        (-1.0, ModbusField(register=1)),
        (700.0, ModbusField(register=1, scale_factor=0.01)),
        (1.0, ModbusField(register=1, data_type="float32")),
    ],
)
def test_to_raw_rejects_what_doesnt_fit(value, field):
    with pytest.raises(ValueError):
        to_raw(value, field)
