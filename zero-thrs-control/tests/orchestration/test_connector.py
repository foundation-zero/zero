from asyncio import create_task, sleep
from datetime import datetime
from typing import Annotated
from unittest import mock

import pytest
from aiomqtt import Client, Topic

from tests.orchestration.simples import (
    SimpleInOut,
    SimpleSimulation,
)
from thrs.input_output.base import (
    CombinedValues,
    Stamped,
    ThrsValues,
    component_meta,
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

settings = Config()  # type: ignore


class ValuesWithTopics(ThrsValues):
    go_with_the: FlowSensor
    go_with_the_topic: Annotated[FlowSensor, component_meta(topic="flow_topic")]


class TestPartialMqttMapping:
    def test_split_to_topics(self):
        mapping = PartialMqttMapping(ValuesWithTopics, "base", "module")
        flow_sensor = FlowSensor(
            flow=Stamped.stamp(10.0), temperature=Stamped.stamp(25.0)
        )
        flow_sensor2 = FlowSensor(
            flow=Stamped.stamp(11.0), temperature=Stamped.stamp(25.0)
        )
        model = ValuesWithTopics(
            go_with_the=flow_sensor, go_with_the_topic=flow_sensor2
        )

        topics = mapping.split_to_topics(model)

        assert "base/module/go-with-the" in topics
        assert "base/flow_topic" in topics
        topic = topics["base/module/go-with-the"]
        assert FlowSensor.model_validate_json(topic) == flow_sensor
        topic2 = topics["base/flow_topic"]
        assert FlowSensor.model_validate_json(topic2) == flow_sensor2

    def test_subscribe_topic(self):
        mapping_no_suffix = PartialMqttMapping(ValuesWithTopics, "base", "module")

        assert mapping_no_suffix.subscribe_topics() == {
            "base/module/+",
            "base/flow_topic",
        }

    def test_builder(self):
        mapping = PartialMqttMapping(SimpleInOut, "base", "module")

        flow_sensor = FlowSensor(
            flow=Stamped.stamp(15.0), temperature=Stamped.stamp(30.0)
        )
        mapping.handle_message(
            "base/module/go-with-the", flow_sensor.model_dump_json(by_alias=True)
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

    def test_subscribe_topic(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")

        assert mapping.subscribe_topics() == set("sensors/data")

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

        assert "/module1/go-with-the" in topics
        assert topics["/module1/go-with-the"] == flow_sensor.model_dump_json(
            by_alias=True
        )

    def test_subscribe_topic(self):
        clss = {"module1": SimpleInOut}
        mapping_no_suffix = ModuleMqttMapping(clss)

        assert mapping_no_suffix.subscribe_topics() == {"/module1/+"}

    def test_builder(self):
        clss = {"module1": SimpleInOut}
        mapping = ModuleMqttMapping(clss)

        flow_sensor = FlowSensor(
            flow=Stamped.stamp(50.0), temperature=Stamped.stamp(5.0)
        )
        mapping.handle_message(
            "/module1/go-with-the", flow_sensor.model_dump_json(by_alias=True)
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
    connector = MqttConnector(
        SimpleSimulation(datetime.now()),
        mqtt_client,
        mqtt_client2,
        "test_topic_prefix",
        {"simple": SimpleInOut},
        {"simple": SimpleInOut},
        SimpleInOut,
    )
    running = create_task(connector.run())
    await sleep(0)

    control_values = CombinedValues(
        values={
            "simple": SimpleInOut(
                go_with_the=FlowSensor(
                    flow=Stamped.stamp(1), temperature=Stamped.stamp(2)
                )
            )
        }
    )

    try:
        first_result = await connector.transceive(control_values)

        data = first_result.values["simple"]
        assert isinstance(data, SimpleInOut)
        assert data.go_with_the.flow.value == 1
        assert data.go_with_the.temperature.value == 2

        await sleep(0.005)
        second_result = await connector.transceive(control_values)

        data = second_result.values["simple"]
        assert isinstance(data, SimpleInOut)
        assert data.go_with_the.flow.value == 1
        assert data.go_with_the.temperature.value == 2

        await sleep(0.1)
        third_result = await connector.transceive(control_values)

        data = third_result.values["simple"]
        assert isinstance(data, SimpleInOut)
        assert data.go_with_the.flow.value == 1
        assert data.go_with_the.temperature.value == 2
    finally:
        running.cancel()


@pytest.fixture
def mock_mqtt_client() -> mock.AsyncMock:
    mock_mqtt_client = mock.AsyncMock(Client)

    async def receive_messages(
        connector: MqttControlConnector, messages: dict[str, ThrsValues]
    ):
        async def return_messages():
            for topic, payload in messages.items():
                yield mock.Mock(
                    topic=Topic(topic),
                    payload=payload.model_dump_json(),
                )

        mock_mqtt_client.messages = return_messages()

        await connector._listen_to_sensors()

    mock_mqtt_client.receive_messages = receive_messages

    return mock_mqtt_client


def sensor_value(flow: int, temperature: int):
    return FlowSensor(flow=Stamped.stamp(flow), temperature=Stamped.stamp(temperature))


def combined_values(sensor1: FlowSensor, sensor2: FlowSensor):
    return CombinedValues(
        values={
            "module": ValuesWithTopics(go_with_the=sensor1, go_with_the_topic=sensor2)
        }
    )


async def test_mqttcontrol_connector(mock_mqtt_client):
    """Check MqttControlConnector

    We are checking:
     - if splitting into different topics work
     - that the topics are correct.
     - that the suffixes are correct
     - That sending and receiving (in order) is correct
    """
    connector = MqttControlConnector(
        mock_mqtt_client,
        "topic_prefix",
        {"module": ValuesWithTopics},
        {"module": ValuesWithTopics},
        "Command",
    )

    # Fake running since we can't properly deal with mock_mqtt_client.messages
    connector._running = True

    # Act
    empty_result = await connector.transceive(
        combined_values(sensor_value(1, 2), sensor_value(3, 4))
    )
    assert not empty_result.values

    # Fake receiving messages
    await mock_mqtt_client.receive_messages(
        connector,
        {
            "topic_prefix/module/go-with-the": sensor_value(1, 2),
            "topic_prefix/flow_topic": sensor_value(3, 4),
        },
    )

    first_result = await connector.transceive(
        combined_values(sensor_value(4, 8), sensor_value(5, 9))
    )

    data = first_result.values["module"]
    assert isinstance(data, ValuesWithTopics)
    assert data.go_with_the.flow.value == 1
    assert data.go_with_the.temperature.value == 2
    assert data.go_with_the_topic.flow.value == 3
    assert data.go_with_the_topic.temperature.value == 4

    # Fake receiving messages
    await mock_mqtt_client.receive_messages(
        connector,
        {
            "topic_prefix/module/go-with-the": sensor_value(4, 8),
            "topic_prefix/flow_topic": sensor_value(5, 9),
        },
    )

    second_result = await connector.transceive(
        combined_values(sensor_value(16, 32), sensor_value(17, 33))
    )

    data = second_result.values["module"]
    assert isinstance(data, ValuesWithTopics)
    assert data.go_with_the.flow.value == 4
    assert data.go_with_the.temperature.value == 8
    assert data.go_with_the_topic.flow.value == 5
    assert data.go_with_the_topic.temperature.value == 9

    assert mock_mqtt_client.publish.call_args_list == [
        mock.call("topic_prefix/module/go-with-the/Command", mock.ANY, qos=1),
        mock.call("topic_prefix/flow_topic/Command", mock.ANY, qos=1),
        mock.call("topic_prefix/module/go-with-the/Command", mock.ANY, qos=1),
        mock.call("topic_prefix/flow_topic/Command", mock.ANY, qos=1),
        mock.call("topic_prefix/module/go-with-the/Command", mock.ANY, qos=1),
        mock.call("topic_prefix/flow_topic/Command", mock.ANY, qos=1),
    ]
