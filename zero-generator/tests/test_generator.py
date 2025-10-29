import asyncio
import json

import pytest
from aiomqtt import Client as MqttClient
from pytest import fixture

from generator.main import DataGenerator


async def _mqtt_client(settings):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client_send = fixture(_mqtt_client)
mqtt_client_receive = fixture(_mqtt_client)


@pytest.mark.asyncio
async def test_generator(mqtt_client_send, mqtt_client_receive):
    received_messages = []
    await mqtt_client_receive.subscribe("test", qos=1)

    async def _receive():
        async for message in mqtt_client_receive.messages:
            received_messages.append(message)

    receive = asyncio.create_task(_receive())

    config = [
        {
            "topic": "test",
            "interval": 0.1,
            "values": {
                "justanint": "int",
                "awa": ["int", 0, 90],
                "aws": ["float", 0, 30],
                "pcs_mode": ["enum", ["propulsion", "idle", "docked"]],
            },
        }
    ]

    data_gen = DataGenerator(mqtt_client=mqtt_client_send)
    send = asyncio.create_task(data_gen.generate(config))

    try:
        await asyncio.sleep(0.2)
        assert any(
            m.topic.value == "test"
            and json.loads(m.payload.decode("utf-8").replace("'", '"')).keys()
            == {"justanint", "awa", "aws", "pcs_mode"}
            for m in received_messages
        )
    finally:
        send.cancel()
        receive.cancel()
