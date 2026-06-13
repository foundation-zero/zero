from asyncio import create_task, sleep
from datetime import datetime
from typing import cast
from unittest import mock

import pytest
from aiomqtt import Client, Topic

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
    def test_split_to_topics(self):
        mapping = PartialMqttMapping(SimpleInOut)
        flow_sensor = FlowSensor(
            flow=Stamped.stamp(10.0), temperature=Stamped.stamp(25.0)
        )
        model = SimpleInOut(go_with_the=flow_sensor)

        topics = mapping.split_to_topics(model)

        assert "go-with-the" in topics
        topic = topics["go-with-the"]
        assert FlowSensor.model_validate_json(topic) == flow_sensor

    def test_has(self):
        mapping = PartialMqttMapping(SimpleInOut)

        assert mapping.has("go-with-the")
        assert not mapping.has("nonexistent")

    def test_subscribe_topic(self):
        mapping_no_suffix = PartialMqttMapping(SimpleInOut)

        assert mapping_no_suffix.subscribe_topic() == "+"

    def test_builder(self):
        mapping = PartialMqttMapping(SimpleInOut)

        flow_sensor = FlowSensor(
            flow=Stamped.stamp(15.0), temperature=Stamped.stamp(30.0)
        )
        mapping.handle_message(
            "go-with-the", flow_sensor.model_dump_json(by_alias=True)
        )
        assert mapping.result() == SimpleInOut(go_with_the=flow_sensor)


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

    def test_builder(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")
        model = SimpleInOut(
            go_with_the=FlowSensor(
                flow=Stamped.stamp(15.0), temperature=Stamped.stamp(30.0)
            )
        )
        mapping.handle_message("sensors/data", model.model_dump_json(by_alias=True))
        assert mapping.result() == model


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

        assert mapping_no_suffix.subscribe_topic() == "+/+"

    def test_builder(self):
        clss = {"module1": SimpleInOut}
        mapping = ModuleMqttMapping(clss)

        flow_sensor = FlowSensor(
            flow=Stamped.stamp(50.0), temperature=Stamped.stamp(5.0)
        )
        mapping.handle_message(
            "module1/go-with-the", flow_sensor.model_dump_json(by_alias=True)
        )
        result = mapping.result()
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


@pytest.fixture
def mock_mqtt_client() -> mock.AsyncMock:
    mock_mqtt_client = mock.AsyncMock(Client)

    mock_mqtt_client.message_queue = []

    async def return_messages():
        for m in mock_mqtt_client.message_queue:
            yield m

    mock_mqtt_client.messages = return_messages()

    return mock_mqtt_client


async def test_mqttcontrol_connector_topic_suffix(mock_mqtt_client):
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
        mock_mqtt_client,
        "topic_prefix/simple",
        module.sensor_values_clss,
        module.control_values_clss,
        "Command",
    )

    sensor_data = FlowSensor(flow=Stamped.stamp(1), temperature=Stamped.stamp(2))
    control_values = CombinedValues(
        values={"simple": SimpleInOut(go_with_the=sensor_data)}
    )

    # Fake running since we can't properly deal with mock_mqtt_client.messages
    connector._running = True

    empty_result = await connector.transceive(control_values)
    assert not empty_result.sensor_values.values
    assert mock_mqtt_client.publish.call_args_list == [
        mock.call("topic_prefix/simple/simple/go-with-the/Command", mock.ANY, qos=1)
    ]

    # Fake receiving messages
    mock_mqtt_client.message_queue = [
        mock.Mock(
            topic=Topic("topic_prefix/simple/simple/go-with-the"),
            payload=sensor_data.model_dump_json(),
        )
    ]
    await connector._listen_to_sensors()

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
        first_result.sensor_values.values["simple"].go_with_the.temperature.value == 2
    )
