import pytest
from zero_modbus_bridge.bit_ops import float_to_lsw_registers
from zero_modbus_bridge.reader import ModbusReader
from zero_modbus_bridge.settings import ModbusSettings

from zero_hull_temperature.addresses import (
    HULL_TEMPERATURE_TOPIC,
    HullTemperature,
    HullTemperaturesModel,
)


@pytest.fixture
def modbus_settings():
    return ModbusSettings(modbus_host="localhost", modbus_port=11502)


@pytest.fixture
def modbus_client(modbus_settings):
    return modbus_settings.modbus_client()


@pytest.mark.asyncio
async def test_reader_reads_float32_registers(modbus_settings, modbus_client):
    """ModbusReader reads float32 values via AnnotationModbusTopic."""
    reader = ModbusReader(modbus_client, [HULL_TEMPERATURE_TOPIC])
    server = modbus_settings.modbus_server()
    server.start()
    try:
        modbus_client.open()
        for field in HULL_TEMPERATURE_TOPIC.fields:
            if field.data_type == "float32":
                server.data_bank.set_holding_registers(
                    field.register, float_to_lsw_registers(20.0)
                )
        results = list(reader.read_all())
        assert len(results) == 1
        _, payload = results[0]
        assert isinstance(payload, HullTemperaturesModel)
        # alias fields are present via by_alias
        dumped = payload.model_dump(by_alias=True)
        assert any(v == 20.0 for v in dumped.values())
        assert len(dumped) == 46
    finally:
        server.stop()


def test_mapping_to_mqtt_payload():
    """MappingPublisher wraps read-model into nested publish-model."""
    read = HullTemperaturesModel(s_94455001_26=20.0, s_94455001_27=18.5)
    wrapped = HullTemperature(temperatures=read)
    assert wrapped.temperatures.s_94455001_26 == 20.0
    assert wrapped.model_dump(by_alias=True) == {
        "temperatures": {"94455001-26": 20.0, "94455001-27": 18.5, **{k: None for k in wrapped.model_dump(by_alias=True)["temperatures"] if k not in ("94455001-26", "94455001-27")}}
    }


def test_hull_temperatures_model_alias():
    """Serialization uses wire serial numbers, python names via populate_by_name."""
    m = HullTemperaturesModel.model_validate({"94455001-26": 21.0})
    assert m.s_94455001_26 == 21.0
    assert m.model_dump(by_alias=True)["94455001-26"] == 21.0
    assert "s_94455001_26" in m.model_dump(by_alias=False)


def test_topic_has_46_fields():
    assert len(HULL_TEMPERATURE_TOPIC.fields) == 46
