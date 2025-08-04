from asyncio import create_task
from aiomqtt import Client as MqttClient
import pytest
from zero_hull_temperature.addresses import PROBE_ADDRESSES
from zero_hull_temperature.bit_ops import float_to_lsw_registers
from zero_hull_temperature.mqtt import Temperatures
from zero_hull_temperature.reader import RelaySwitchingTemperatureReader, TemperatureReader
from zero_hull_temperature.settings import ModbusSettings
from zero_hull_temperature.stub import Stub

async def _mqtt_client():
    async with MqttClient("localhost", port=1883) as mqtt:
        yield mqtt

mqtt_client = pytest.fixture(_mqtt_client)
mqtt_client2 = pytest.fixture(_mqtt_client)
mqtt_client3 = pytest.fixture(_mqtt_client)

@pytest.fixture
def modbus_settings():
    return ModbusSettings(modbus_host="localhost", modbus_port=11502)

async def test_modbus_read_temperatures(modbus_settings):
    server = modbus_settings.modbus_server()
    try:
        server.start()
        for address in PROBE_ADDRESSES:
            server.data_bank.set_holding_registers(address.register, float_to_lsw_registers(20.0))
        temperatures = await TemperatureReader(modbus_settings.modbus_client()).read_temperatures()

        assert len(temperatures) == len(PROBE_ADDRESSES)
        for reading in temperatures:
            assert reading.temperature == 20.0

    finally:
        server.stop()


async def test_mqtt_switching(mqtt_client, mqtt_client2, modbus_settings):
    client_mqtt = mqtt_client
    server_mqtt = mqtt_client2

    stub = Stub(server_mqtt, modbus_settings.modbus_server(), "test/topic", "$.path", 20.0)
    
    reader = RelaySwitchingTemperatureReader(modbus_settings.modbus_client(), client_mqtt, "test/topic", "$.path", "hull-temperature/temperatures")

    run_stub = create_task(await stub.run())

    try:
        temperatures = await reader.read_temperatures()

        assert len(temperatures) == len(PROBE_ADDRESSES)
        for reading in temperatures:
            assert reading.temperature == 20.0
    finally:
        await stub.disable_modbus()
        run_stub.cancel()

async def test_mqtt_sending(mqtt_client, mqtt_client2, mqtt_client3, modbus_settings):
    client_mqtt = mqtt_client
    server_mqtt = mqtt_client2
    test_client = mqtt_client3

    await test_client.subscribe("hull-temperature/temperatures")

    stub = Stub(server_mqtt, modbus_settings.modbus_server(), "test/topic", "$.path", 20.0)
    
    reader = RelaySwitchingTemperatureReader(modbus_settings.modbus_client(), client_mqtt, "test/topic", "$.path", "hull-temperature/temperatures")

    run_stub = create_task(await stub.run())

    try:
        await reader.step()

        message = await anext(test_client.messages)
        assert message.topic.matches("hull-temperature/temperatures")
        result = Temperatures.model_validate_json(message.payload)
        for reading in result.temperatures:
            assert reading.temperature == 20.0
    finally:
        await stub.disable_modbus()
        run_stub.cancel()

    
