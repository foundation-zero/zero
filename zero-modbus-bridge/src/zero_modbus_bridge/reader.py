"""Modbus reader: yields model instances from annotated topics."""

import logging
from typing import Any, Iterator

from pydantic import BaseModel
from pyModbusTCP.client import ModbusClient

from zero_modbus_bridge.bit_ops import lsw_registers_to_float
from zero_modbus_bridge.io import ModbusField, ModbusTopic

logger = logging.getLogger(__name__)


class ModbusReader:
    """Reads Modbus registers and yields topic/payload pairs.

    Topics are expected to provide both ``fields`` and ``converter``.
    Annotation-driven topics are pre-compiled into those two values by
    ``AnnotationModbusTopic.model_post_init``.
    """

    def __init__(self, modbus: ModbusClient, topics: list[ModbusTopic]):
        self._modbus = modbus
        self._topics = topics

    def ensure_open(self) -> bool:
        """Open the underlying Modbus connection if needed.

        Returns ``True`` when the connection is (already) open.
        """
        if self._modbus.is_open:
            return True
        return bool(self._modbus.open())

    def read_all(self) -> Iterator[tuple[str, Any]]:
        """Read every topic once and yield ``(topic_name, payload)``."""
        if not self._modbus.is_open:
            raise ValueError("Modbus connection is not open")
        for topic in self._topics:
            self._modbus.unit_id = topic.unit_id
            try:
                payload = self.read_topic(topic)
                if payload is not None:
                    yield topic.topic, payload
            except Exception:
                logger.exception("Failed to read topic %s", topic.topic)

    def read_topic[T: BaseModel](self, topic: ModbusTopic[T]) -> T:
        reads = self._read_normalized(topic, topic.fields)
        values = [(reg, raw) for reg, raw in reads]
        return topic.converter(values)

    def _read_normalized(
        self,
        topic: ModbusTopic,
        fields: list[ModbusField],
    ) -> list[tuple[int | None, int | float | bool | None]]:
        reads: list[tuple[int | None, int | float | bool | None]] = []
        for field in fields:
            reg = _resolve_register(field, topic.start_register)
            try:
                raw = self._read_field(field, reg)
                if field.validator is not None and not field.validator(raw):
                    raw = None
                reads.append((reg, raw))
            except ValueError:
                logger.warning(
                    "Failed to read register %s for topic %s", reg, topic.topic
                )
                reads.append((None, None))
        return reads

    def _read_field(
        self, field: ModbusField, register: int
    ) -> int | float | bool | None:
        if field.data_type == "float32" and field.count == 2:
            return self._read_float32(register)
        if field.modbus_type == "coil":
            return self._read_coil(register)
        return self._read_uint16(register)

    def _read_float32(self, register: int) -> float | None:
        regs = self._modbus.read_holding_registers(register, 2)
        if regs and len(regs) == 2:
            return lsw_registers_to_float(regs)
        raise ValueError(f"Failed to read float32 from register {register}")

    def _read_coil(self, register: int) -> bool | None:
        value = self._modbus.read_coils(register, 1)
        if value and len(value) >= 1:
            return bool(value[0])
        raise ValueError(f"Failed to read coil from address {register}")

    def _read_uint16(self, register: int) -> int | None:
        value = self._modbus.read_holding_registers(register, 1)
        if value:
            return value[0]
        raise ValueError(f"Failed to read register {register}")


def _resolve_register(field: ModbusField, start_register: int) -> int:
    if field.offset is not None:
        return start_register + field.offset
    if field.register is not None:
        return field.register
    raise ValueError("ModbusField has neither register nor offset")
