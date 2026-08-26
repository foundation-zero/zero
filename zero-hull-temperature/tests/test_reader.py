import pytest
from zero_modbus_bridge.bit_ops import float_to_lsw_registers
from zero_modbus_bridge.reader import ModbusReader
from zero_modbus_bridge.settings import ModbusSettings

from zero_hull_temperature.addresses import (
    HULL_TEMPERATURE_FIELDS,
    HULL_TEMPERATURE_TOPIC,
    hull_temp_converter,
)


@pytest.fixture
def modbus_settings():
    return ModbusSettings(modbus_host="localhost", modbus_port=11502)


@pytest.fixture
def modbus_client(modbus_settings):
    return modbus_settings.modbus_client()


@pytest.mark.asyncio
async def test_reader_reads_float32_registers(modbus_settings, modbus_client):
    """ModbusReader reads float32 values from a local Modbus server via HULL_TEMPERATURE_FIELDS."""
    reader = ModbusReader(modbus_client, [HULL_TEMPERATURE_TOPIC])
    server = modbus_settings.modbus_server()
    server.start()
    try:
        modbus_client.open()
        for field in HULL_TEMPERATURE_FIELDS:
            if field.data_type == "float32":
                server.data_bank.set_holding_registers(
                    field.register, float_to_lsw_registers(20.0)
                )
        results = list(reader.read_all())
        assert len(results) == 1
        _, payload = results[0]
        data = payload  # payload is a HullTemperature instance
        temps = data.temperatures
        assert any(v == 20.0 for v in temps.values())
    finally:
        server.stop()


def test_hull_temp_converter():
    """_hull_temp_converter builds valid HullTemperature."""
    values: list[tuple[int | None, int | float | bool | None]] = [
        (9203, 20.0),
        (9205, 18.5),
    ]
    result = hull_temp_converter(values)
    # Fields are keyed by sensor name from HULL_TEMP_SENSORS
    assert isinstance(result.temperatures, dict)


def test_hull_temp_converter_empty():
    """Empty input produces full dict with None values."""
    result = hull_temp_converter([])
    assert all(v is None for v in result.temperatures.values())
    assert len(result.temperatures) == 46  # 46 sensor probes, no diagnostics


def test_hull_temp_converter_handles_none_register():
    """Converter ignores entries with register=None."""
    result = hull_temp_converter([(None, 42.0)])
    assert all(v is None for v in result.temperatures.values())


def test_hull_temp_converter_handles_none_value():
    """Converter maps register with value=None to None key."""
    result = hull_temp_converter([(9203, None)])
    # The sensor at register 9203 should still appear, but as None
    # Keys are sensor serial numbers (e.g. 94455001-26 for register 9203)
    assert any(k.startswith("94455001-") for k in result.temperatures)
    assert all(v is None for v in result.temperatures.values())
