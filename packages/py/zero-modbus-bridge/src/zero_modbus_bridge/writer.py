"""Modbus writer: writes registers on a client it may share with a ``ModbusReader``.

pyModbusTCP isn't thread-safe: callers sharing a client run reads and writes
on one thread (``ModbusBridge`` does).
"""

import logging

from pyModbusTCP.client import ModbusClient

logger = logging.getLogger(__name__)

type RegisterWrite = tuple[int, int]
"""``(register, raw value)``: one write of a single holding register."""


class ModbusWriteError(Exception):
    """A write did not reach the device; later writes of the batch were skipped."""


class ModbusWriter:
    def __init__(self, modbus: ModbusClient):
        self._modbus = modbus

    def write(self, unit_id: int, writes: list[RegisterWrite]) -> None:
        """Write ``writes`` to ``unit_id`` in order, stopping at the first failure.

        Devices that apply a batch on a final register (a commit or selection
        register) apply nothing when an earlier write fails.
        """
        if not self._modbus.is_open and not self._modbus.open():
            raise ModbusWriteError("Modbus connection unavailable")
        self._modbus.unit_id = unit_id
        for register, value in writes:
            if not self._modbus.write_single_register(register, value):
                raise ModbusWriteError(
                    f"Failed to write {value} to register {register} of unit {unit_id}"
                )
            logger.debug("Wrote %s to register %s of unit %s", value, register, unit_id)
