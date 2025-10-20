import asyncio
import json

import pytest
from aiomqtt import Client as MqttClient
from pytest import fixture

from loads.control import Control


async def _mqtt_client(settings):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client_receive = fixture(_mqtt_client)
mqtt_client_send = fixture(_mqtt_client)
mqtt_client_external = fixture(_mqtt_client)


@pytest.mark.asyncio
async def test_control_determine_conditions(mqtt_client_receive, mqtt_client_send):
    """Test the Control process logic for determining the conditions."""
    process = Control(mqtt_client=mqtt_client_receive)
    control = asyncio.create_task(await process.run())

    try:
        await asyncio.sleep(1)
        await mqtt_client_send.publish(
            "loads/sensor_input",
            '{"awa": 45.0, "aws": 12.0, "pcs_mode": {"fwd": "propulsion", "aft": "propulsion"}, "sails": ["full-main-sail", "main-blade", "full-mizzen-sail"]}',
        )
        await process.wait_for_values()
        case = await process._determine_conditions()

        assert case.sea_state == "wet"
    finally:
        control.cancel()


@pytest.mark.asyncio
async def test_control_end_to_end(
    mqtt_client_receive, mqtt_client_send, mqtt_client_external
):
    """Test the Control process end-to-end with MQTT messages"""
    process = Control(mqtt_client=mqtt_client_receive)
    control = asyncio.create_task(await process.run())

    await mqtt_client_external.subscribe("loads/conditions", qos=1)
    received_messages = []

    async def _receive():
        async for message in mqtt_client_external.messages:
            received_messages.append(message)

    receive = asyncio.create_task(_receive())

    try:
        await mqtt_client_send.publish(
            "loads/sensor_input",
            '{"awa": 45.0, "aws": 12.0, "pcs_mode": {"fwd": "propulsion", "aft": "propulsion"}, "sails": ["full-main-sail", "main-blade", "full-mizzen-sail"]}',
        )
        await process.wait_for_values()
        await asyncio.sleep(0.1)
        assert next(
            True
            for m in received_messages
            if m.topic.value == "loads/conditions"
            and json.loads(m.payload)
            == {
                "sea_state": "wet",
                "awa": 45.0,
                "aws": 12.0,
                "pcs_mode": {"fwd": "propulsion", "aft": "propulsion"},
                "sails": ["full-main-sail", "main-blade", "full-mizzen-sail"],
            }
        )
    finally:
        control.cancel()
        receive.cancel()
