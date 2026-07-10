import asyncio
import json
from asyncio import create_task
from unittest.mock import MagicMock

import pytest
from aiomqtt import Client as MqttClient
from fastapi.testclient import TestClient
from pytest import fixture

from domestic_control.app import data_collection
from domestic_control.config import Settings
from domestic_control.messages import Amplifier
from domestic_control.mqtt import DataCollection
from domestic_control.services.av import (
    AFT_PDU,
    FWD_PDU,
    Av,
    AvControl,
    Gude,
)
from domestic_control.services.stubs.av import AV_STUB_TELEMETRY_INTERVAL, AvStub


@fixture
def settings():
    return Settings()  # type: ignore


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

    stub_run = create_task(await stub.run())
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

    stub_task = create_task(await stub.run())

    await av.set_amplifier("owners-cockpit", True)
    assert await expect_result(lambda: stub.read_port(AFT_PDU, 1), True, 0.1)

    await av.set_amplifier("office", True)
    assert await expect_result(lambda: stub.read_port(FWD_PDU, 1), True, 0.1)

    stub_task.cancel()


@pytest.mark.timeout(10)
async def test_av_control_receive(mqtt_client, mqtt_client2, mqtt_client3):
    av_control = AvControl(Gude(mqtt_client), DataCollection(mqtt_client))
    stub = AvStub(mqtt_client2)

    await mqtt_client3.subscribe("domestic/amplifiers")

    control_task = create_task(await av_control.run())
    stub_task = create_task(await stub.run())
    stub.set_port(AFT_PDU, 1, True)

    async for message in mqtt_client3.messages:
        if message.topic.value == "domestic/amplifiers" and isinstance(
            message.payload, str | bytes
        ):
            msg = json.loads(message.payload)
            if msg["id"] == "owners-cockpit":
                assert msg["on"]
                break

    stub_task.cancel()
    control_task.cancel()


@pytest.mark.timeout(10)
async def test_av_through_gq(mqtt_client, test_app):
    data_collection_mock = MagicMock(spec=DataCollection)
    await mqtt_client.subscribe("domestic/amplifiers")
    client = TestClient(test_app)
    test_app.dependency_overrides[data_collection] = lambda: data_collection_mock

    response = client.post(
        "/graphql",
        json={
            "query": """mutation { setAmplifiers(ids: "owners-cabin", on: true) { code success message } }"""
        },
    )
    await asyncio.sleep(0.05)
    assert response.status_code == 200

    data_collection_mock.send.assert_called_once_with(
        Amplifier(id="owners-cabin", on=True)
    )
