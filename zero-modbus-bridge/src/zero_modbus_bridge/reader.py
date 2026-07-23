"""Modbus reader: yields model instances from annotated topics."""

import logging
from typing import Any, AsyncIterator

from pyModbusTCP.client import ModbusClient
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_fixed

from zero_modbus_bridge.bit_ops import lsw_registers_to_float
from zero_modbus_bridge.io import ModbusField, ModbusTopic, apply_modbus_field

logger = logging.getLogger(__name__)

# Invalid Float32 sentinel used by Schneider PowerTag and Moore HES controllers.
# 0xFFC00000 → registers [0xFFC0, 0x0000]
INVALID_FLOAT_SENTINEL = 0xFFC00000


def _is_invalid_float(regs: list[int]) -> bool:
    """Check if two registers represent the invalid Float32 sentinel."""
    sentinel_high = (INVALID_FLOAT_SENTINEL >> 16) & 0xFFFF
    sentinel_low = INVALID_FLOAT_SENTINEL & 0xFFFF
    return len(regs) == 2 and regs[0] == sentinel_high and regs[1] == sentinel_low


class ModbusReader:
    """Reads Modbus registers and yields topic/payload pairs.

    Topics are expected to provide both ``fields`` and ``converter``.
    Annotation-driven topics are pre-compiled into those two values by
    ``ModbusTopic.model_post_init``.
    """

    def __init__(self, modbus: ModbusClient, topics: list[ModbusTopic]):
        self._modbus = modbus
        self._topics = topics

    async def read_all(self) -> AsyncIterator[tuple[str, Any]]:
        """Read every topic once and yield ``(topic_name, payload)``."""
        for topic in self._topics:
            self._modbus.unit_id = topic.unit_id
            try:
                payload = self.read_topic(topic)
                if payload is not None:
                    yield topic.topic, payload
            except Exception:
                logger.exception("Failed to read topic %s", topic.topic)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def read_topic[T: BaseModel](self, topic: ModbusTopic[T]) -> T | None:
        if topic.converter is None:
            logger.warning("No converter configured for topic %s", topic.topic)
            return None
        if not topic.fields:
            logger.warning("No fields configured for topic %s", topic.topic)
            return None

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
                reads.append((reg, self._read_field(field, reg)))
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
            if _is_invalid_float(regs):
                return None
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


def _apply_field(
    raw: int | float | bool | None, field: ModbusField
) -> int | float | bool | None:
    return apply_modbus_field(raw, field)
