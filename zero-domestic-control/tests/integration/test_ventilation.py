import asyncio
import json
from asyncio import TaskGroup, create_task

from aiomqtt import Client as MqttClient
from pyModbusTCP.client import ModbusClient
from pytest import fixture

from domestic_control.config import Settings
from domestic_control.messages import RoomCo2Setpoint
from domestic_control.mqtt import ControlReceive, ControlSend, DataCollection
from domestic_control.services.stubs.ventilation import VentilationStub
from domestic_control.services.ventilation import (
    Ventilation,
    VentilationControl,
    VentilationInterface,
)


@fixture
def settings():
    return Settings()  # type: ignore


async def _mqtt_client(settings):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


@fixture
async def modbus_client(settings):
    return ModbusClient(
        host=settings.ventilation_host,
        port=settings.ventilation_port,
        auto_open=True,
    )


mqtt_client = fixture(_mqtt_client)
mqtt_client2 = fixture(_mqtt_client)
mqtt_client3 = fixture(_mqtt_client)


async def test_control_receive(settings, mqtt_client, mqtt_client2):
    """Test that the ControlSend messages reach ControlReceive."""
    control_send = ControlSend(mqtt_client)
    control_receive = ControlReceive(mqtt_client2)

    await control_receive.listen()

    await control_send.send_room_co2_setpoint("owners-cabin", 850)
    await asyncio.sleep(1)
    async for message in control_receive.messages:
        assert message.id == "owners-cabin"
        assert isinstance(message, RoomCo2Setpoint)
        assert message.co2 == 850
        break


async def test_ventilation_adjustment_forwarded_to_data_collection(
    settings, modbus_client, mqtt_client, mqtt_client2, mqtt_client3
):
    """Test that ventilation adjustments are forwarded to domestic/ventilation."""
    stub = VentilationStub(settings.ventilation_host, settings.ventilation_port)
    ventilation_interface = VentilationInterface(modbus_client)
    data_collection = DataCollection(mqtt_client)
    control_receiver = ControlReceive(mqtt_client2)
    ventilation_control = VentilationControl(
        control_receiver, ventilation_interface, data_collection
    )

    await mqtt_client3.subscribe("domestic/ventilation", qos=1)
    received_messages = []

    async def _receive():
        async for message in mqtt_client3.messages:
            received_messages.append(message)

    stub_run = create_task(stub.run())
    receive = create_task(_receive())
    ventilation_run = create_task(await ventilation_control.run())

    try:
        await asyncio.sleep(0.1)
        ventilation_interface.write_room_co2_setpoint("dutch-cabin", 850)
        await asyncio.sleep(0.2)
        assert next(
            True
            for m in received_messages
            if m.topic.value == "domestic/ventilation"
            and _pick_json(m.payload, ["id", "co2_setpoint"])
            == {"id": "dutch-cabin", "co2_setpoint": 850.0}
        )
    finally:
        stub_run.cancel()
        ventilation_run.cancel()
        receive.cancel()


async def test_setting_setpoints(
    settings, modbus_client, mqtt_client, mqtt_client2, mqtt_client3
):
    """Test that the setpoint is set correctly in ventilation and sent to domestic/ventilation."""
    stub = VentilationStub(settings.ventilation_host, settings.ventilation_port)
    ventilation_interface = VentilationInterface(modbus_client)
    data_collection = DataCollection(mqtt_client)
    control_send = ControlSend(mqtt_client)
    control_receiver = ControlReceive(mqtt_client2)
    ventilation = Ventilation(control_send)
    ventilation_control = VentilationControl(
        control_receiver, ventilation_interface, data_collection
    )

    await mqtt_client3.subscribe("domestic/ventilation", qos=1)
    received_messages = []

    async def _receive():
        async for message in mqtt_client3.messages:
            received_messages.append(message)

    receive = create_task(_receive())
    stub_run = create_task(stub.run())
    ventilation_run = create_task(await ventilation_control.run())

    try:
        await ventilation.write_room_co2_setpoint("french-cabin", 900)
        await asyncio.sleep(0.2)
        assert ventilation_interface.read_room_co2_setpoint("french-cabin") == 900
        assert next(
            True
            for m in received_messages
            if m.topic.value == "domestic/ventilation"
            and _pick_json(m.payload, ["id", "co2_setpoint"])
            == {"id": "french-cabin", "co2_setpoint": 900.0}
        )
    finally:
        stub_run.cancel()
        ventilation_run.cancel()
        receive.cancel()


def _pick_json(message: str, fields: list[str]) -> dict:
    """Pick specific fields from a JSON message."""
    data = json.loads(message)
    picked_data = {key: value for key, value in data.items() if key in fields}
    return picked_data


async def test_multiple_mutations(
    settings: Settings, modbus_client, mqtt_client, mqtt_client2, mqtt_client3
):
    """When multiple mutations are made simultaneously to ventilation, test if they are forwarded correctly and not overwritten."""
    stub = VentilationStub(settings.ventilation_host, settings.ventilation_port)
    ventilation_interface = VentilationInterface(modbus_client)
    data_collection = DataCollection(mqtt_client)
    control_send = ControlSend(mqtt_client)
    control_receiver = ControlReceive(mqtt_client2)
    ventilation = Ventilation(control_send)
    ventilation_control = VentilationControl(
        control_receiver, ventilation_interface, data_collection
    )

    stub_run = create_task(stub.run())
    ventilation_run = create_task(await ventilation_control.run())

    try:
        await asyncio.sleep(0.1)
        async with TaskGroup() as tg:
            for room_id in ["dutch-cabin", "californian-lounge"]:
                tg.create_task(
                    ventilation.write_room_co2_setpoint(room=room_id, co2=950)
                )
        await asyncio.sleep(1)

        assert ventilation_interface.read_room_co2_setpoint("dutch-cabin") == 950
        assert ventilation_interface.read_room_co2_setpoint("californian-lounge") == 950
    finally:
        stub_run.cancel()
        ventilation_run.cancel()
