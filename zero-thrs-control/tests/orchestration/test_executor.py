from asyncio import create_task, sleep
import asyncio
from datetime import datetime
from typing import cast

from aiomqtt import Client
import pytest
from thrs.orchestration.module import ModuleDescription, CombinedModule
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    Stamped,
)
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.orchestration.config import Config
from thrs.orchestration.executor import MqttExecutor
from tests.orchestration.simples import (
    SimpleAlarms,
    SimpleControl,
    SimpleExecutor,
    SimpleInOut,
    SimpleParameters,
)


settings = Config()  # type: ignore


async def _mqtt_client():
    async with Client(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client = pytest.fixture(_mqtt_client)
mqtt_client2 = pytest.fixture(_mqtt_client)


async def test_mqtt_executor(mqtt_client, mqtt_client2):
    simple_executor = SimpleExecutor(datetime.now())
    executor = MqttExecutor(
        simple_executor,
        mqtt_client,
        mqtt_client2,
        f"{settings.mqtt_topic_prefix}/simple",
        CombinedModule(
            {
                "simple": ModuleDescription(
                    SimpleInOut,
                    SimpleInOut,
                    SimpleParameters,
                    SimpleControl,
                    SimpleAlarms,
                )
            },
            cast(type[SimulationInputs], SimpleInOut),
            cast(type[SimulationValues], SimpleInOut),
        ),
    )
    await executor.start()
    running = create_task(executor.run())
    await sleep(0)

    try:
        empty_result = await executor.tick(
            CombinedValues(
                values={
                    "simple": SimpleInOut(
                        go_with_the=FlowSensor(
                            flow=Stamped.stamp(1), temperature=Stamped.stamp(2)
                        )
                    )
                }
            )
        )
        assert not empty_result.sensor_values.values
        await sleep(0.005)
        first_result = await executor.tick(
            CombinedValues(
                values={
                    "simple": SimpleInOut(
                        go_with_the=FlowSensor(
                            flow=Stamped.stamp(1), temperature=Stamped.stamp(2)
                        )
                    )
                }
            )
        )
        assert isinstance(first_result.sensor_values.values["simple"], SimpleInOut)
        assert first_result.sensor_values.values["simple"].go_with_the.flow.value == 1
        assert (
            first_result.sensor_values.values["simple"].go_with_the.temperature.value
            == 2
        )
        await sleep(0.1)
        second_result = await executor.tick(
            CombinedValues(
                {
                    "simple": SimpleInOut(
                        go_with_the=FlowSensor(
                            flow=Stamped.stamp(1), temperature=Stamped.stamp(2)
                        )
                    )
                }
            )
        )
        assert isinstance(second_result.sensor_values.values["simple"], SimpleInOut)
        assert second_result.sensor_values.values["simple"].go_with_the.flow.value == 1
        assert (
            second_result.sensor_values.values["simple"].go_with_the.temperature.value
            == 2
        )
    finally:
        running.cancel()
