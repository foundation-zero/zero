"""Modbus register <-> Python type helpers."""

import math
import struct

from zero_modbus_bridge.io import RawModbusValue


def lsw_registers_to_float(regs: list[int]) -> float:
    """
    Convert two Modbus registers to a float.
    Assumes big-endian word order (ABCD), as used by the HES converter.
    """
    b = struct.pack(">HH", *regs)  # 2 words
    val = struct.unpack(">f", b)[0]  # Read as float
    return val


def float_to_lsw_registers(value: float) -> list[int]:
    """
    Convert a float to two Modbus registers.
    Returns a list of two integers.
    """
    b = struct.pack(">f", value)  # Pack as float
    regs = struct.unpack(">HH", b)  # Unpack as two words
    return list(regs)


def uint16_to_int16(raw: int) -> int:
    """Read a raw register as a two's complement signed value: 65535 -> -1."""
    return raw - 0x10000 if raw & 0x8000 else raw


def int16_to_uint16(value: int) -> int:
    """Store a signed value as a raw two's complement register: -1 -> 65535."""
    return value & 0xFFFF


def is_finite_float(raw: RawModbusValue) -> bool:
    """Validator for float fields: reject non-finite values (NaN sentinels, ±inf).

    Schneider PowerTag and Moore HES controllers mark invalid readings with NaN
    sentinels that decode to ``math.nan``. Returning ``False`` makes the reader
    drop the value (emit ``None``) rather than publishing it.
    """
    return isinstance(raw, float) and math.isfinite(raw)
