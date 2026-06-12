from asyncio import create_task, sleep
from datetime import datetime
from typing import cast

import pytest
from aiomqtt import Client

from tests.orchestration.simples import (
    SimpleAlarms,
    SimpleControl,
    SimpleInOut,
    SimpleMode,
    SimpleParameters,
    SimpleSimulation,
)
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    Stamped,
)
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.orchestration.config import Config
from thrs.orchestration.connector import MqttConnector, MqttControlConnector
from thrs.orchestration.module import CombinedModule, ModuleDescription

settings = Config()  # type: ignore


async def _mqtt_client():
    async with Client(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client = pytest.fixture(_mqtt_client)
mqtt_client2 = pytest.fixture(_mqtt_client)


async def test_mqtt_connector(mqtt_client, mqtt_client2):
    simple_simulation = SimpleSimulation(datetime.now())
    module = CombinedModule(
        {
            "simple": ModuleDescription(
                SimpleInOut,
                SimpleInOut,
                SimpleParameters,
                SimpleControl,
                SimpleMode,
                SimpleAlarms,
            )
        },
        cast(type[SimulationInputs], SimpleInOut),
        cast(type[SimulationValues], SimpleInOut),
    )
    connector = MqttConnector(
        simple_simulation,
        mqtt_client,
        mqtt_client2,
        f"{settings.mqtt_topic_prefix}/simple",
        module.sensor_values_mqtt_mapping,
        module.control_values_mqtt_mapping,
        module.simulation_output_mqtt_mapping,
    )
    await connector.start()
    running = create_task(connector.run())
    await sleep(0)

    try:
        first_result = await connector.tick(
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
        await sleep(0.005)
        second_result = await connector.tick(
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
        assert isinstance(second_result.sensor_values.values["simple"], SimpleInOut)
        assert second_result.sensor_values.values["simple"].go_with_the.flow.value == 1
        assert (
            second_result.sensor_values.values["simple"].go_with_the.temperature.value
            == 2
        )
        await sleep(0.1)
        third_result = await connector.tick(
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
        assert isinstance(third_result.sensor_values.values["simple"], SimpleInOut)
        assert third_result.sensor_values.values["simple"].go_with_the.flow.value == 1
        assert (
            third_result.sensor_values.values["simple"].go_with_the.temperature.value
            == 2
        )
    finally:
        running.cancel()


async def test_boat_connector_echoes_controls_to_sensors(mqtt_client):
    module = CombinedModule(
        {
            "simple": ModuleDescription(
                SimpleInOut,
                SimpleInOut,
                SimpleParameters,
                SimpleControl,
                SimpleMode,
                SimpleAlarms,
            )
        },
        cast(type[SimulationInputs], SimpleInOut),
        cast(type[SimulationValues], SimpleInOut),
    )
    connector = MqttControlConnector(
        mqtt_client,
        f"{settings.mqtt_topic_prefix}/simple",
        module.sensor_values_mqtt_mapping,
        module.control_values_mqtt_mapping,
    )
    await connector.start()
    running = create_task(connector.run())
    await sleep(0)

    try:
        empty_result = await connector.tick(
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

        first_result = await connector.tick(
            CombinedValues(
                values={
                    "simple": SimpleInOut(
                        go_with_the=FlowSensor(
                            flow=Stamped.stamp(4), temperature=Stamped.stamp(8)
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

        second_result = await connector.tick(
            CombinedValues(
                values={
                    "simple": SimpleInOut(
                        go_with_the=FlowSensor(
                            flow=Stamped.stamp(16), temperature=Stamped.stamp(32)
                        )
                    )
                }
            )
        )
        assert isinstance(second_result.sensor_values.values["simple"], SimpleInOut)
        assert second_result.sensor_values.values["simple"].go_with_the.flow.value == 4
        assert (
            second_result.sensor_values.values["simple"].go_with_the.temperature.value
            == 8
        )
    finally:
        running.cancel()
