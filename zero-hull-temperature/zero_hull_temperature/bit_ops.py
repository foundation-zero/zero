import struct


def lsw_registers_to_float(regs):
    """
    Convert two Modbus registers to a float.
    Assumes little-endian word order.
    """
    b = struct.pack("<HH", *regs)  # 2 words
    val = struct.unpack("<f", b)[0]  # Read as float
    return val

def float_to_lsw_registers(value):
    """
    Convert a float to two Modbus registers.
    Returns a list of two integers.
    """
    b = struct.pack("<f", value)  # Pack as float
    regs = struct.unpack("<HH", b)  # Unpack as two words
    return list(regs)
