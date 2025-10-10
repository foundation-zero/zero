import pytest
import asyncio

from asyncio import create_task
from aiomqtt import Client as MqttClient
from pytest import fixture

from loads.control import LoadsControl


async def _mqtt_client(settings):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client_receive = fixture(_mqtt_client)
mqtt_client_send = fixture(_mqtt_client)


@pytest.mark.asyncio
async def test_control(mqtt_client_receive, mqtt_client_send):
    """Test the LoadsControl process end-to-end with MQTT messages"""
    process = LoadsControl(mqtt_client=mqtt_client_receive)
    control = create_task(process.run())

    await asyncio.sleep(1)
    # We send two messages. Control should take only the last one into account
    await mqtt_client_send.publish(
        "loads/risingwave/conditions",
        '{"awa": 0, "aws": 0, "pcs_mode": {"fwd": "idle", "aft": "idle"}, "sails": ["full-main-sail"]}',
    )
    await mqtt_client_send.publish(
        "loads/risingwave/conditions",
        '{"awa": 45.0, "aws": 12.0, "pcs_mode": {"fwd": "propulsion", "aft": "propulsion"}, "sails": ["full-main-sail", "main-blade", "full-mizzen-sail"]}',
    )
    await asyncio.sleep(1)
    case = await process.determine_load_case()

    assert case.sea_state == "wet"
    assert case.awa == 45.0
    assert case.aws == 12.0
    assert case.pcs_mode.fwd.value == "propulsion"
    assert case.pcs_mode.aft.value == "propulsion"
    assert case.sails == ["full-main-sail", "main-blade", "full-mizzen-sail"]

    control.cancel()
