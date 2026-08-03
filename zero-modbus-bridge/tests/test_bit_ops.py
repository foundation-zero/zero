from zero_modbus_bridge.bit_ops import (
    float_to_lsw_registers,
    is_finite_float,
    lsw_registers_to_float,
)


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
