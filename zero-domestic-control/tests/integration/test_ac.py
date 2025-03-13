from asyncio import create_task
import asyncio

from aiomqtt import Client as MqttClient
from pytest import fixture

from zero_domestic_control.config import Settings
from zero_domestic_control.mqtt import ControlReceive, ControlSend, DataCollection
from zero_domestic_control.services.ac import Ac, AcControl, TermodinamicaAc
from zero_domestic_control.services.stubs.ac import TermodinamicaStub
from zero_domestic_control.services.ac.thrs import Thrs

from pyModbusTCP.client import ModbusClient


@fixture
def settings():
    return Settings()


async def _mqtt_client(settings):
    async with MqttClient(settings.mqtt_host, 1883) as client:
        yield client


@fixture
async def modbus_client(settings):
    return ModbusClient(
        host=settings.termodinamica_host,
        port=settings.termodinamica_port,
        auto_open=True,
    )


mqtt_client = fixture(_mqtt_client)
mqtt_client2 = fixture(_mqtt_client)
mqtt_client3 = fixture(_mqtt_client)


async def test_control_receive(settings, mqtt_client, mqtt_client2):
    control_send = ControlSend(mqtt_client)
    control_receive = ControlReceive(mqtt_client2)

    await control_receive.listen()

    await control_send.send_room_setpoint("owners-cabin", 20)
    await asyncio.sleep(1)
    async for message in control_receive.messages:
        assert message.id == "owners-cabin"
        assert message.temperature == 20
        break


async def test_termodinamica_adjustment_forwarded_to_thrs(
    settings, modbus_client, mqtt_client, mqtt_client2, mqtt_client3
):
    stub = TermodinamicaStub(settings.termodinamica_host, settings.termodinamica_port)
    termodinamica = TermodinamicaAc(modbus_client)
    thrs = Thrs(mqtt_client)
    data_collection = DataCollection(mqtt_client)
    control_receiver = ControlReceive(mqtt_client2)
    ac_control = AcControl(control_receiver, termodinamica, thrs, data_collection)

    await mqtt_client3.subscribe("thrs/#", qos=1)
    await mqtt_client3.subscribe("domestic/rooms", qos=1)
    received_messages = []

    async def _receive():
        async for message in mqtt_client3.messages:
            received_messages.append(message)

    stub_run = create_task(stub.run())
    await asyncio.sleep(0.1)
    termodinamica.write_room_temperature_setpoint("owners-cabin", 20)

    receive = create_task(_receive())
    ac_run = create_task(ac_control.run())

    try:
        await asyncio.sleep(0.1)
        thrs_message = next(
            m
            for m in received_messages
            if m.topic.value == "thrs/room-temperature-setpoint/owners-cabin"
        )
        assert thrs_message.payload == b'{"temperature":20.0}'
        assert next(
            True
            for m in received_messages
            if m.topic.value == "domestic/rooms"
            and m.payload == b'{"id":"owners-cabin","temperature_setpoint":20.0}'
        )
    finally:
        stub_run.cancel()
        ac_run.cancel()
        receive.cancel()


async def test_setting_setpoint(
    settings, modbus_client, mqtt_client, mqtt_client2, mqtt_client3
):
    stub = TermodinamicaStub(settings.termodinamica_host, settings.termodinamica_port)
    termodinamica = TermodinamicaAc(modbus_client)
    thrs = Thrs(mqtt_client)
    data_collection = DataCollection(mqtt_client)
    control_send = ControlSend(mqtt_client)
    control_receiver = ControlReceive(mqtt_client2)
    ac = Ac(control_send)
    ac_control = AcControl(control_receiver, termodinamica, thrs, data_collection)

    await mqtt_client3.subscribe("thrs/#", qos=1)
    await mqtt_client3.subscribe("domestic/rooms", qos=1)
    received_messages = []

    async def _receive():
        async for message in mqtt_client3.messages:
            received_messages.append(message)

    receive = create_task(_receive())
    stub_run = create_task(stub.run())
    ac_run = create_task(ac_control.run())

    try:
        await asyncio.sleep(0.1)
        await ac.write_room_temperature_setpoint("owners-cabin", 20)
        await asyncio.sleep(0.2)
        assert termodinamica.read_room_temperature_setpoint("owners-cabin") == 20
        assert next(
            True
            for m in received_messages
            if m.topic.value == "thrs/room-temperature-setpoint/owners-cabin"
            and m.payload == b'{"temperature":20.0}'
        )
        assert next(
            True
            for m in received_messages
            if m.topic.value == "domestic/rooms"
            and m.payload == b'{"id":"owners-cabin","temperature_setpoint":20.0}'
        )
    finally:
        stub_run.cancel()
        ac_run.cancel()
        receive.cancel()
