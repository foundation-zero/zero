from asyncio import create_task
import asyncio
from typing import Callable

from aiomqtt import Client as MqttClient
from pytest import fixture

from zero_domestic_control.config import Settings
from zero_domestic_control.mqtt import ControlReceive, ControlSend, DataCollection
from zero_domestic_control.services.ac import Ac, AcControl, TermodinamicaAc
from zero_domestic_control.services.stubs.ac import TermodinamicaStub
from zero_domestic_control.services.ac.thrs import Thrs

from pyModbusTCP.client import ModbusClient
import json


@fixture
def settings():
    return Settings()


async def _mqtt_client(settings):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
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
    """Test that the ControlSend messages reach ControlReceive"""
    control_send = ControlSend(mqtt_client)
    control_receive = ControlReceive(mqtt_client2)

    await control_receive.listen()

    await control_send.send_room_temperature_setpoint("owners-cabin", 10)
    await asyncio.sleep(1)
    async for message in control_receive.messages:
        assert message.id == "owners-cabin"
        assert message.temperature == 10
        break


async def test_termodinamica_adjustment_forwarded_to_thrs(
    settings, modbus_client, mqtt_client, mqtt_client2, mqtt_client3
):
    """Test that the Termodinamica adjustments are forwarded to THRS and domestic/ac topics"""
    stub = TermodinamicaStub(settings.termodinamica_host, settings.termodinamica_port)
    termodinamica = TermodinamicaAc(modbus_client)
    thrs = Thrs(mqtt_client)
    data_collection = DataCollection(mqtt_client)
    control_receiver = ControlReceive(mqtt_client2)
    ac_control = AcControl(control_receiver, termodinamica, thrs, data_collection)

    await mqtt_client3.subscribe("thrs/#", qos=1)
    await mqtt_client3.subscribe("domestic/ac", qos=1)
    received_messages = []

    async def _receive():
        async for message in mqtt_client3.messages:
            received_messages.append(message)

    stub_run = create_task(stub.run())
    receive = create_task(_receive())
    ac_run = create_task(await ac_control.run())

    try:
        await asyncio.sleep(0.1)
        termodinamica.write_room_temperature_setpoint("dutch-cabin", 15)
        await asyncio.sleep(0.2)
        assert next(
            True
            for m in received_messages
            if m.topic.value == "thrs/room-temperature-setpoint/dutch-cabin"
            and json.loads(m.payload).get("temperature") == 15.0
        )
        assert next(
            True
            for m in received_messages
            if m.topic.value == "domestic/ac"
            and _pick_json(m.payload, ["id", "temperature_setpoint"])
            == {"id": "dutch-cabin", "temperature_setpoint": 15.0}
        )
    finally:
        stub_run.cancel()
        ac_run.cancel()
        receive.cancel()


async def test_setting_setpoints(
    settings, modbus_client, mqtt_client, mqtt_client2, mqtt_client3
):
    """Test that the setpoint is set correctly in Termodinamica and sent to THRS and domestic/ac topics"""
    stub = TermodinamicaStub(settings.termodinamica_host, settings.termodinamica_port)
    termodinamica = TermodinamicaAc(modbus_client)
    thrs = Thrs(mqtt_client)
    data_collection = DataCollection(mqtt_client)
    control_send = ControlSend(mqtt_client)
    control_receiver = ControlReceive(mqtt_client2)
    ac = Ac(control_send)
    ac_control = AcControl(control_receiver, termodinamica, thrs, data_collection)

    await mqtt_client3.subscribe("thrs/#", qos=1)
    await mqtt_client3.subscribe("domestic/ac", qos=1)
    received_messages = []

    async def _receive():
        async for message in mqtt_client3.messages:
            received_messages.append(message)

    receive = create_task(_receive())
    stub_run = create_task(stub.run())
    ac_run = create_task(await ac_control.run())

    try:
        await ac.write_room_temperature_setpoint("french-cabin", 20)
        await asyncio.sleep(0.2)
        assert termodinamica.read_room_temperature_setpoint("french-cabin") == 20
        assert next(
            True
            for m in received_messages
            if m.topic.value == "thrs/room-temperature-setpoint/french-cabin"
            and json.loads(m.payload).get("temperature") == 20.0
        )
        assert next(
            True
            for m in received_messages
            if m.topic.value == "domestic/ac"
            and _pick_json(m.payload, ["id", "temperature_setpoint"])
            == {"id": "french-cabin", "temperature_setpoint": 20.0}
        )
        received_messages = []
        await asyncio.sleep(0.1)
        await ac.write_room_humidity_setpoint("italian-cabin", 0.5)
        await asyncio.sleep(0.2)
        assert termodinamica.read_room_humidity_setpoint("italian-cabin") == 0.5
        assert next(
            True
            for m in received_messages
            if m.topic.value == "thrs/room-humidity-setpoint/italian-cabin"
            and json.loads(m.payload).get("humidity") == 0.5
        )
        assert next(
            True
            for m in received_messages
            if m.topic.value == "domestic/ac"
            and _pick_json(m.payload, ["id", "humidity_setpoint"])
            == {"id": "italian-cabin", "humidity_setpoint": 0.5}
        )
        received_messages = []
        await asyncio.sleep(0.1)
        await ac.write_room_co2_setpoint("californian-lounge", 0.4)
        await asyncio.sleep(0.2)
        assert termodinamica.read_room_co2_setpoint("californian-lounge") == 0.4
        assert next(
            True
            for m in received_messages
            if m.topic.value == "thrs/room-co2-setpoint/californian-lounge"
            and json.loads(m.payload).get("co2") == 0.4
        )
        assert next(
            True
            for m in received_messages
            if m.topic.value == "domestic/ac"
            and _pick_json(m.payload, ["id", "co2_setpoint"])
            == {"id": "californian-lounge", "co2_setpoint": 0.4}
        )
    finally:
        stub_run.cancel()
        ac_run.cancel()
        receive.cancel()


def _pick_json(message: str, fields: list[str]) -> dict:
    """Pick specific fields from a JSON message."""
    data = json.loads(message)
    picked_data = {key: value for key, value in data.items() if key in fields}
    return picked_data
