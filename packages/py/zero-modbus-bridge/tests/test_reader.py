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
    mock_modbus.read_coils.return_value = [1]

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
    mock_modbus.read_holding_registers.return_value = [0x4248, 0x0000]

    topic = AnnotationModbusTopic(
        topic="test/e",
        model=FloatModel,
        extra_fields={"room": "Lounge"},
    )
    reader = ModbusReader(mock_modbus, [topic])
    result = reader.read_topic(topic)
    assert result is not None
    assert result.room == "Lounge"


class _SocketDroppingGateway:
    """A PowerTag Link that drops the TCP socket on a dead unit id.

    A live unit returns data; a dead unit times out and closes the socket
    (``is_open`` goes False) until it is reopened.
    """

    def __init__(self, live_units: set[int]):
        self._live_units = live_units
        self.unit_id = 0
        self.is_open = True
        self.reopens = 0

    def open(self) -> bool:
        self.is_open = True
        self.reopens += 1
        return True

    def read_holding_registers(self, register: int, count: int):
        if not self.is_open:
            return None  # socket is closed -> spurious failure
        if self.unit_id in self._live_units:
            return [0x4248, 0x0000]  # -> 50.0 as float32
        self.is_open = False  # dead unit: time out and drop the socket
        return None


def test_read_all_reconnects_after_dead_unit_drops_socket():
    """A dead unit id must not poison the live topics that follow it."""
    gateway = _SocketDroppingGateway(live_units={1, 3})
    topics = [
        AnnotationModbusTopic(topic="t/1", model=FloatModel, unit_id=1),
        AnnotationModbusTopic(topic="t/2", model=FloatModel, unit_id=2),  # dead
        AnnotationModbusTopic(topic="t/3", model=FloatModel, unit_id=3),
    ]
    reader = ModbusReader(gateway, topics)  # type: ignore[arg-type]

    results = {name: payload for name, payload in reader.read_all()}

    # Both live topics read despite the dead unit closing the socket between them.
    assert results["t/1"].value == 50.0
    assert results["t/3"].value == 50.0
    # The dead unit still yields a null-valued payload, not a lost topic.
    assert results["t/2"].value is None
    # The socket was reopened after the dead unit dropped it.
    assert gateway.reopens >= 1


class _UnreachableGateway:
    """Gateway whose socket can never be opened - the whole unit is down."""

    def __init__(self):
        self.unit_id = 0
        self.is_open = False
        self.open_attempts = 0

    def open(self) -> bool:
        self.open_attempts += 1
        return False


def test_read_all_stops_on_unreachable_gateway():
    """A down gateway yields nothing and isn't reopened once per topic."""
    gateway = _UnreachableGateway()
    topics = [
        AnnotationModbusTopic(topic=f"t/{i}", model=FloatModel, unit_id=i)
        for i in range(1, 6)
    ]
    reader = ModbusReader(gateway, topics)  # type: ignore[arg-type]

    assert list(reader.read_all()) == []
    # Breaks on the first failed open instead of retrying every remaining topic.
    assert gateway.open_attempts == 1
