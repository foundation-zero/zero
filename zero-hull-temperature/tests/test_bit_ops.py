from zero_hull_temperature.bit_ops import float_to_lsw_registers, lsw_registers_to_float


def test_lsw_registers_to_float():
    # Example from docs/3094 Hull Temperature Sensors Configuration.docx page 13 screenshot (not the C# example, that is endianness dependent)
    assert lsw_registers_to_float([0xD4E6, 0x419D]) == 19.728954315185547


def test_float_to_lsw_registers():
    assert float_to_lsw_registers(19.728954315185547) == [0xD4E6, 0x419D]
