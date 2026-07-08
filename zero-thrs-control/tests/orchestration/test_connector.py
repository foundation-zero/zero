import json
from typing import Annotated
from unittest import mock

import pytest
from aiomqtt import Client, Topic
from pydantic import computed_field

from tests.orchestration.simples import SimpleInOut
from thrs.input_output.base import (
    CombinedValues,
    Stamped,
    ThrsValues,
    component_meta,
    computed_meta,
)
from thrs.input_output.definitions.sensor import FlowSensor, TemperatureDelta
from thrs.orchestration.comms import (
    DirectMqttMapping,
    ModuleMqttMapping,
    MqttConnector,
    PartialMqttMapping,
)


class ValuesWithTopics(ThrsValues):
    go_with_the: FlowSensor
    go_with_the_topic: Annotated[
        FlowSensor, component_meta(topic_override="flow-topic")
    ]

    @computed_field(json_schema_extra=computed_meta(topic_override="flow-delta"))
    @property
    def flow_delta(self) -> TemperatureDelta:
        return TemperatureDelta.from_temperature_sensors(
            temperature_supply=self.go_with_the.temperature,
            temperature_return=self.go_with_the_topic.temperature,
        )


class TestPartialMqttMapping:
    def test_split_to_topics(self):
        mapping = PartialMqttMapping(ValuesWithTopics, "base", "module")
        flow_sensor = FlowSensor(
            flow=Stamped.stamp(10.0), temperature=Stamped.stamp(25.0)
        )
        flow_sensor2 = FlowSensor(
            flow=Stamped.stamp(11.0), temperature=Stamped.stamp(27.0)
        )
        model = ValuesWithTopics(
            go_with_the=flow_sensor, go_with_the_topic=flow_sensor2
        )

        topics = mapping.split_to_topics(model)

        assert "base/module/go-with-the" in topics
        assert "base/flow-topic" in topics
        topic = topics["base/module/go-with-the"]
        assert FlowSensor.model_validate_json(topic) == flow_sensor
        topic2 = topics["base/flow-topic"]
        assert FlowSensor.model_validate_json(topic2) == flow_sensor2

    def test_split_to_topics_computed(self):
        mapping = PartialMqttMapping(
            ValuesWithTopics, "base", "module", only_computed_fields=True
        )
        flow_sensor = FlowSensor(
            flow=Stamped.stamp(10.0), temperature=Stamped.stamp(25.0)
        )
        flow_sensor2 = FlowSensor(
            flow=Stamped.stamp(11.0), temperature=Stamped.stamp(27.0)
        )
        model = ValuesWithTopics(
            go_with_the=flow_sensor, go_with_the_topic=flow_sensor2
        )

        topics = mapping.split_to_topics(model)

        assert "base/flow-delta" in topics
        topic = topics["base/flow-delta"]
        assert json.loads(topic) == {"DeltaT": {"Value": 2.0, "TimeStamp": mock.ANY}}

    def test_subscribe_topic(self):
        mapping_no_suffix = PartialMqttMapping(ValuesWithTopics, "base", "module")

        assert mapping_no_suffix.subscribe_topics() == {
            "base/module/+",
            "base/flow-topic",
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

        assert mapping.subscribe_topics() == {"sensors/data"}

    def test_builder(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")
        model = SimpleInOut(
            go_with_the=FlowSensor(
                flow=Stamped.stamp(15.0), temperature=Stamped.stamp(30.0)
            )
        )
        mapping.handle_message("sensors/data", model.model_dump_json(by_alias=True))
        assert mapping.result() == model


class TestCombinedMqttMapping:
    def test_split_to_topics(self):
        clss = {"module1": SimpleInOut}
        mapping = ModuleMqttMapping(clss, PartialMqttMapping)
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
        mapping_no_suffix = ModuleMqttMapping(clss, PartialMqttMapping)

        assert mapping_no_suffix.subscribe_topics() == {"/module1/+"}

    def test_builder(self):
        clss = {"module1": SimpleInOut}
        mapping = ModuleMqttMapping(clss, PartialMqttMapping)

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


@pytest.fixture
async def mqtt_client(settings):
    async with Client(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


@pytest.fixture
def mock_mqtt_client() -> mock.AsyncMock:
    mock_mqtt_client = mock.AsyncMock(Client)

    async def receive_messages(
        connector: MqttConnector, messages: dict[str, ThrsValues]
    ):
        async def return_messages():
            for topic, payload in messages.items():
                yield mock.Mock(topic=Topic(topic), payload=payload.model_dump_json())

        mock_mqtt_client.messages = return_messages()

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


async def test_mqtt_connector_publisher_uses_mapping(mock_mqtt_client):
    connector = MqttConnector(mock_mqtt_client)
    publisher = connector._create_publisher(
        ModuleMqttMapping(
            {"module": ValuesWithTopics},
            PartialMqttMapping,
            "devices_topic_prefix",
            "Command",
        )
    )

    first_values = combined_values(sensor_value(1, 2), sensor_value(3, 4))
    second_values = combined_values(sensor_value(4, 8), sensor_value(5, 9))
    third_values = combined_values(sensor_value(16, 32), sensor_value(17, 33))

    await publisher(first_values)
    await publisher(second_values)
    await publisher(third_values)

    published_topics = {
        call.args[0] for call in mock_mqtt_client.publish.call_args_list
    }
    assert published_topics == {
        "devices_topic_prefix/module/go-with-the/Command",
        "devices_topic_prefix/flow-topic/Command",
    }

    assert mock_mqtt_client.publish.call_args_list == [
        mock.call(
            "devices_topic_prefix/module/go-with-the/Command",
            mock.ANY,
            qos=1,
            retain=False,
        ),
        mock.call(
            "devices_topic_prefix/flow-topic/Command",
            mock.ANY,
            qos=1,
            retain=False,
        ),
        mock.call(
            "devices_topic_prefix/module/go-with-the/Command",
            mock.ANY,
            qos=1,
            retain=False,
        ),
        mock.call(
            "devices_topic_prefix/flow-topic/Command",
            mock.ANY,
            qos=1,
            retain=False,
        ),
        mock.call(
            "devices_topic_prefix/module/go-with-the/Command",
            mock.ANY,
            qos=1,
            retain=False,
        ),
        mock.call(
            "devices_topic_prefix/flow-topic/Command",
            mock.ANY,
            qos=1,
            retain=False,
        ),
    ]
    assert mock_mqtt_client.publish.await_count == 6
    assert all(
        "flow-delta" not in call.args[0]
        for call in mock_mqtt_client.publish.call_args_list
    )

    calls = mock_mqtt_client.publish.call_args_list
    assert len(calls) == 6
    for call in calls:
        assert call.kwargs["qos"] == 1
        assert call.kwargs["retain"] is False

    payloads = [FlowSensor.model_validate_json(call.args[1]) for call in calls]
    expected_values = [
        (1, 2),
        (3, 4),
        (4, 8),
        (5, 9),
        (16, 32),
        (17, 33),
    ]
    for payload, (flow, temperature) in zip(payloads, expected_values):
        assert payload.flow.value == flow
        assert payload.temperature.value == temperature

    payload_json = [json.loads(call.args[1]) for call in calls]
    assert payload_json[0] == {
        "Flow": {"Value": 1, "TimeStamp": mock.ANY},
        "Temperature": {"Value": 2, "TimeStamp": mock.ANY},
    }
    assert payload_json[1] == {
        "Flow": {"Value": 3, "TimeStamp": mock.ANY},
        "Temperature": {"Value": 4, "TimeStamp": mock.ANY},
    }
