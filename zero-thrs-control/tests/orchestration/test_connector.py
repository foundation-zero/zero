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
    ThrsValues,
)
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.orchestration.config import Config
from thrs.orchestration.connector import (
    DirectMqttMapping,
    ModuleMqttMapping,
    MqttConnector,
    MqttControlConnector,
    PartialMqttMapping,
)
from thrs.orchestration.module import CombinedModule, ModuleDescription

settings = Config()  # type: ignore


class TestPartialMqttMapping:
    def test_split_to_topics_without_suffix(self):
        mapping = PartialMqttMapping(SimpleInOut)
        flow_sensor = FlowSensor(
            flow=Stamped.stamp(10.0), temperature=Stamped.stamp(25.0)
        )
        model = SimpleInOut(go_with_the=flow_sensor)

        topics = mapping.split_to_topics(model)

        assert "go-with-the" in topics
        topic = topics["go-with-the"]
        assert FlowSensor.model_validate_json(topic) == flow_sensor

    def test_split_to_topics_with_suffix(self):
        mapping = PartialMqttMapping(SimpleInOut, "sensors")
        flow_sensor = FlowSensor(
            flow=Stamped.stamp(10.0), temperature=Stamped.stamp(25.0)
        )
        model = SimpleInOut(go_with_the=flow_sensor)

        topics = mapping.split_to_topics(model)

        assert "go-with-the/sensors" in topics
        topic = topics["go-with-the/sensors"]
        assert FlowSensor.model_validate_json(topic) == flow_sensor

    def test_has_without_suffix(self):
        mapping = PartialMqttMapping(SimpleInOut)

        assert mapping.has("go-with-the")
        assert not mapping.has("nonexistent")

    def test_has_with_suffix(self):
        mapping = PartialMqttMapping(SimpleInOut, "sensors")

        assert mapping.has("go-with-the/sensors")
        assert not mapping.has("go-with-the")

    def test_subscribe_topic(self):
        mapping_no_suffix = PartialMqttMapping(SimpleInOut)
        mapping_with_suffix = PartialMqttMapping(SimpleInOut, "sensors")

        assert mapping_no_suffix.subscribe_topic() == "+"
        assert mapping_with_suffix.subscribe_topic() == "+/sensors"

    def test_builder(self):
        mapping = PartialMqttMapping(SimpleInOut)
        builder = mapping.builder()

        flow_sensor = FlowSensor(
            flow=Stamped.stamp(15.0), temperature=Stamped.stamp(30.0)
        )
        builder.input("go-with-the", flow_sensor.model_dump_json(by_alias=True))
        assert builder.result() == SimpleInOut(go_with_the=flow_sensor)


class TestDirectMqttMapping:
    def test_split_to_topics(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")
        model = SimpleInOut(
            go_with_the=FlowSensor(
                flow=Stamped.stamp(25.0), temperature=Stamped.stamp(1.2)
            )
        )
        topics = mapping.split_to_topics(model)

        assert "sensors/data" in topics
        assert topics["sensors/data"] == model.model_dump_json(by_alias=True)

    def test_has(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")

        assert mapping.has("sensors/data")
        assert not mapping.has("other/topic")

    def test_subscribe_topic(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")

        assert mapping.subscribe_topic() == "sensors/data"

    def test_builder_not_implemented(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")
        with pytest.raises(NotImplementedError):
            mapping.builder()


class ModulesValues(ThrsValues):
    module1: SimpleInOut


class TestCombinedMqttMapping:
    def test_split_to_topics(self):
        clss = {"module1": SimpleInOut}
        mapping = ModuleMqttMapping(clss)
        flow_sensor = FlowSensor(
            flow=Stamped.stamp(25.0), temperature=Stamped.stamp(1.2)
        )
        combined_values = CombinedValues(
            values={"module1": SimpleInOut(go_with_the=flow_sensor)}
        )

        topics = mapping.split_to_topics(combined_values)

        assert "module1/go-with-the" in topics
        assert topics["module1/go-with-the"] == flow_sensor.model_dump_json(
            by_alias=True
        )

    def test_has(self):
        clss = {"module1": SimpleInOut}
        mapping = ModuleMqttMapping(clss)

        assert mapping.has("module1/go-with-the")
        assert not mapping.has("module2/go-with-the")

    def test_subscribe_topic(self):
        clss = {"module1": SimpleInOut}
        mapping_no_suffix = ModuleMqttMapping(clss)
        mapping_with_suffix = ModuleMqttMapping(clss, "sensors")

        assert mapping_no_suffix.subscribe_topic() == "+/+"
        assert mapping_with_suffix.subscribe_topic() == "+/+/sensors"

    def test_builder(self):
        clss = {"module1": SimpleInOut}
        mapping = ModuleMqttMapping(clss)
        builder = mapping.builder()

        flow_sensor = FlowSensor(
            flow=Stamped.stamp(50.0), temperature=Stamped.stamp(5.0)
        )
        builder.input("module1/go-with-the", flow_sensor.model_dump_json(by_alias=True))
        result = builder.result()
        assert result == CombinedValues(
            {"module1": SimpleInOut(go_with_the=flow_sensor)}
        )


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
        module.sensor_values_clss,
        module.control_values_clss,
        module.simulation_outputs_cls,
    )
    await connector.start()
    running = create_task(connector.run())
    await sleep(0)

    try:
        first_result = await connector.transceive(
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
        second_result = await connector.transceive(
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
        third_result = await connector.transceive(
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
        module.sensor_values_clss,
        module.control_values_clss,
    )
    await connector.start()
    running = create_task(connector.run())
    await sleep(0)

    try:
        empty_result = await connector.transceive(
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

        first_result = await connector.transceive(
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

        second_result = await connector.transceive(
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
