import asyncio
import json

import pytest
from aiomqtt import Client as MqttClient
from pytest import fixture

import generator.gen as gen
from generator import DataGenerator, GeneratorConfig, create_generator
from generator.base import JSONGenerator


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

    g = JSONGenerator(
        values={
            "justanint": gen.int_(),
            "awa": gen.int_(0, 90),
            "aws": gen.float_(0, 30),
            "pcs_mode": gen.choice(["propulsion", "idle", "docked"]),
        },
    )
    config = [
        GeneratorConfig(
            topic="test",
            interval=1,
            generator=g,
        )
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


def test_create_generator():
    test: dict[gen.GeneratorType, gen.MarpowerGenerator] = {
        "int": gen.int_(),
        "float": gen.float_(),
        "str": gen.str_(),
        "bool": gen.bool_(),
        "timestamp": gen.timestamp(),
        "choice": gen.choice(options=["a", "b"]),
    }

    for type, generator in test.items():
        if type == "choice":
            assert isinstance(
                create_generator(type, options=["a", "b"]), generator.__class__
            )
        else:
            assert create_generator(type).__class__ == generator.__class__
