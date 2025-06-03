from asyncio import create_task
import asyncio
import json
from pytest import fixture
import pytest
from zero_domestic_control.services.av import (
    AFT_PDU,
    FWD_PDU,
    Av,
    AvControl,
    Gude,
)
from zero_domestic_control.services.stubs.av import AV_STUB_TELEMETRY_INTERVAL, AvStub
from zero_domestic_control.config import Settings
from zero_domestic_control.mqtt import DataCollection
from aiomqtt import Client as MqttClient
from fastapi.testclient import TestClient
from zero_domestic_control.app import app


@fixture
def settings():
    return Settings()


async def _mqtt_client(settings):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client = fixture(_mqtt_client)
mqtt_client2 = fixture(_mqtt_client)
mqtt_client3 = fixture(_mqtt_client)


async def expect_result(fn, result, timeout):
    try:
        async with asyncio.timeout(timeout):
            while True:
                if fn() == result:
                    return True
                await asyncio.sleep(0.05)
        return False
    except asyncio.TimeoutError:
        return False
    except Exception as e:
        raise e


@pytest.mark.timeout(10)
async def test_stub(mqtt_client, mqtt_client2):
    stub = AvStub(mqtt_client)

    received = []
    await mqtt_client2.subscribe("de/gudesystems/#", qos=1)

    async def _receive_messages():
        async for message in mqtt_client2.messages:
            received.append(message)

    receive = create_task(_receive_messages())

    stub_run = create_task(stub.run())
    assert await expect_result(lambda: len(received), 2, 1)
    await asyncio.sleep(AV_STUB_TELEMETRY_INTERVAL)
    assert await expect_result(lambda: len(received), 4, 0.5)
    assert received[0].topic.value.startswith("de/gudesystems/epc/")
    assert received[1].topic.value.startswith("de/gudesystems/epc/")

    stub_run.cancel()
    receive.cancel()


@pytest.mark.timeout(10)
async def test_av_send(mqtt_client, mqtt_client2):
    av = Av(Gude(mqtt_client), DataCollection(mqtt_client))
    stub = AvStub(mqtt_client2)

    stub_task = create_task(stub.run())

    await asyncio.sleep(0.1)
    await av.set_amplifier("owners-cockpit", True)
    assert await expect_result(lambda: stub.read_port(AFT_PDU, 1), True, 0.1)

    await av.set_amplifier("office", True)
    assert await expect_result(lambda: stub.read_port(FWD_PDU, 1), True, 0.1)

    stub_task.cancel()


@pytest.mark.timeout(10)
async def test_av_control_receive(mqtt_client, mqtt_client2, mqtt_client3):
    av_control = AvControl(Gude(mqtt_client), DataCollection(mqtt_client))
    stub = AvStub(mqtt_client2)

    await mqtt_client3.subscribe("domestic/rooms")

    control_task = create_task(av_control.run())
    stub_task = create_task(stub.run())
    stub.set_port(AFT_PDU, 1, True)

    async for message in mqtt_client3.messages:
        if message.topic.value == "domestic/rooms" and isinstance(
            message.payload, str | bytes
        ):
            msg = json.loads(message.payload)
            if msg["id"] == "owners-cockpit":
                assert msg["amplifier_on"]
                break

    stub_task.cancel()
    control_task.cancel()


@pytest.mark.timeout(10)
async def test_av_through_gq(mqtt_client):
    await mqtt_client.subscribe("domestic/rooms")
    client = TestClient(app)
    response = client.post(
        "/graphql",
        json={
            "query": """mutation { setAmplifiers(ids: "owners-cabin", on: true) { code success message } }"""
        },
    )

    assert response.status_code == 200

    async for message in mqtt_client.messages:
        if message.topic.value == "domestic/rooms" and isinstance(
            message.payload, str | bytes
        ):
            msg = json.loads(message.payload)
            if msg["id"] == "owners-cabin":
                assert msg["amplifier_on"]
                break
