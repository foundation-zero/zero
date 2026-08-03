from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from tests.conftest import FloatModel, ScaledModel, UintModel
from zero_modbus_bridge.io import (
    AnnotationModbusTopic,
    ConverterModbusTopic,
    ModbusField,
)
from zero_modbus_bridge.reader import (
    ModbusReader,
)


@pytest.mark.asyncio
async def test_reader_annotated_float32_success():
    mock_modbus = MagicMock()
    mock_modbus.read_holding_registers.return_value = [0x4248, 0x0000]

    topic = AnnotationModbusTopic(
        topic="test/f",
        model=FloatModel,
        start_register=3000,
    )
    reader = ModbusReader(mock_modbus, [topic])
    result = reader.read_topic(topic)
    assert result is not None
    assert result.value == 50.0


@pytest.mark.asyncio
async def test_reader_annotated_invalid_float32():
    mock_modbus = MagicMock()
    mock_modbus.read_holding_registers.return_value = [0xFFC0, 0x0000]

    topic = AnnotationModbusTopic(
        topic="test/f",
        model=FloatModel,
        start_register=3000,
    )
    reader = ModbusReader(mock_modbus, [topic])
    result = reader.read_topic(topic)
    assert result is not None
    assert result.value is None


@pytest.mark.asyncio
async def test_reader_annotated_uint16():
    mock_modbus = MagicMock()
    mock_modbus.read_holding_registers.side_effect = [[42], [1]]  # val=42, flag=1
    mock_modbus.read_coils.return_value = [1]

    topic = AnnotationModbusTopic(topic="test/u", model=UintModel)
    reader = ModbusReader(mock_modbus, [topic])
    result = reader.read_topic(topic)
    assert result is not None
    assert result.val == 42
    assert result.flag is True


@pytest.mark.asyncio
async def test_reader_annotated_scaling():
    mock_modbus = MagicMock()
    mock_modbus.read_holding_registers.return_value = [625]

    topic = AnnotationModbusTopic(topic="test/s", model=ScaledModel)
    reader = ModbusReader(mock_modbus, [topic])
    result = reader.read_topic(topic)
    assert result is not None
    assert result.scaled == 25.0


@pytest.mark.asyncio
async def test_reader_annotated_invalid_value_sentinel():
    mock_modbus = MagicMock()
    mock_modbus.read_holding_registers.return_value = [0xFFFF]

    topic = AnnotationModbusTopic(topic="test/u", model=UintModel)
    reader = ModbusReader(mock_modbus, [topic])
    result = reader.read_topic(topic)
    assert result is not None
    assert result.val is None


def test_reader_converter():
    mock_modbus = MagicMock()
    mock_modbus.read_holding_registers.return_value = [100]

    class SumModel(BaseModel):
        sum: float

    def conv(values):
        reg_map = {reg: val for reg, val in values if reg is not None}
        return SumModel(sum=sum(reg_map.values()))

    topic = ConverterModbusTopic(
        topic="test/c",
        model=FloatModel,
        fields=[ModbusField(register=10)],
        converter=conv,
    )
    reader = ModbusReader(mock_modbus, [topic])
    topic, payload = next(reader.read_all())
    assert topic == "test/c"
    assert payload.sum == 100


@pytest.mark.asyncio
async def test_reader_converter_single():
    mock_modbus = MagicMock()
    mock_modbus.read_holding_registers.return_value = [100]

    class SumModel(BaseModel):
        sum: float

    def conv(values):
        reg_map = {reg: val for reg, val in values if reg is not None}
        return SumModel(sum=sum(reg_map.values()))

    topic = ConverterModbusTopic(
        topic="test/c",
        model=FloatModel,
        fields=[ModbusField(register=10)],
        converter=conv,
    )
    reader = ModbusReader(mock_modbus, [topic])
    result = reader.read_topic(topic)
    assert isinstance(result, SumModel)
    assert result.sum == 100


@pytest.mark.asyncio
async def test_reader_extra_fields_merged():
    mock_modbus = MagicMock()
    mock_modbus.read_holding_registers.return_value = [25]

    topic = AnnotationModbusTopic(
        topic="test/e",
        model=FloatModel,
        extra_fields={"room": "Lounge"},
    )
    reader = ModbusReader(mock_modbus, [topic])
    result = reader.read_topic(topic)
    assert result is not None
    assert result.room == "Lounge"
