from asyncio import create_task
import asyncio

from aiomqtt import Client
import pytest
from input_output.base import Stamped
from input_output.definitions.sensor import FlowSensor
from orchestration.config import Config
from orchestration.executor import MqttExecutor
from tests.orchestration.simples import SimpleExecutor, SimpleInOut


settings = Config()  # type: ignore


async def _mqtt_client():
    async with Client(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client = pytest.fixture(_mqtt_client)
mqtt_client2 = pytest.fixture(_mqtt_client)


async def test_mqtt_executor(mqtt_client, mqtt_client2):
    simple_executor = SimpleExecutor()
    executor = MqttExecutor(
        simple_executor,
        mqtt_client,
        mqtt_client2,
        settings.mqtt_sensor_topic,
        SimpleInOut,
        settings.mqtt_control_topic,
        SimpleInOut,
    )
    running = create_task(executor.start())
    await asyncio.sleep(0.1)

    try:
        result = await executor.tick(
            SimpleInOut(
                go_with_the=FlowSensor(
                    flow=Stamped.stamp(1), temperature=Stamped.stamp(2)
                )
            )
        )
        assert result.sensor_values.go_with_the.flow.value == 1
        assert result.sensor_values.go_with_the.temperature.value == 2
    finally:
        running.cancel()
