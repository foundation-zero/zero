import json
from typing import Annotated
from unittest import mock

import pytest
from aiomqtt import Client, Topic
from pydantic import computed_field

from tests.orchestration.simples import (
    SimpleControllerState,
    SimpleInOut,
    SimpleMode,
    SimpleParameters,
)
from thrs.control.switching import AutomationMode
from thrs.input_output.base import (
    CombinedValues,
    Stamped,
    ThrsValues,
    component_meta,
    computed_meta,
)
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.sensor import (
    FlowSensor,
    TemperatureDelta,
    TemperatureSensor,
)
from thrs.orchestration.comms import (
    ControlChannels,
    DirectMqttMapping,
    MergedModuleMqttMapping,
    ModuleMqttMapping,
    MqttConnector,
    PartialMqttMapping,
)
from thrs.orchestration.module import ModuleDescription


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


class MergeSensorValues(ThrsValues):
    pump: FlowSensor
    temperature: TemperatureSensor


class MergeControlValues(ThrsValues):
    pump: Pump
    valve: Valve


def merged_sensor_values() -> CombinedValues:
    return CombinedValues(
        {
            "module": MergeSensorValues(
                pump=FlowSensor(
                    flow=Stamped.stamp(10.0), temperature=Stamped.stamp(20.0)
                ),
                temperature=TemperatureSensor(temperature=Stamped.stamp(30.0)),
            )
        }
    )


def merged_control_values() -> CombinedValues:
    return CombinedValues(
        {
            "module": MergeControlValues(
                pump=Pump(dutypoint=Stamped.stamp(0.4), on=Stamped.stamp(True)),
                valve=Valve(setpoint=Stamped.stamp(0.6)),
            )
        }
    )


def merged_mapping() -> MergedModuleMqttMapping:
    return MergedModuleMqttMapping(
        {"module": MergeSensorValues}, {"module": MergeControlValues}, "base"
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


def _simple_model(flow: float) -> SimpleInOut:
    return SimpleInOut(
        go_with_the=FlowSensor(
            flow=Stamped.stamp(flow), temperature=Stamped.stamp(20.0)
        )
    )


class TestDirectMqttMappingAutoclear:
    def test_default_stays_sticky(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")
        model = _simple_model(1.0)
        mapping.handle_message("sensors/data", model.model_dump_json(by_alias=True))
        assert mapping.result() == model
        assert mapping.result() == model

    def test_result_consumes_once(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data", autoclear=True)
        model = _simple_model(1.0)
        mapping.handle_message("sensors/data", model.model_dump_json(by_alias=True))
        assert mapping.result() == model
        assert mapping.result() is None

    def test_new_message_rearms(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data", autoclear=True)
        first = _simple_model(1.0)
        mapping.handle_message("sensors/data", first.model_dump_json(by_alias=True))
        assert mapping.result() == first
        assert mapping.result() is None
        second = _simple_model(2.0)
        mapping.handle_message("sensors/data", second.model_dump_json(by_alias=True))
        assert mapping.result() == second
        assert mapping.result() is None

    def test_for_module_passes_autoclear(self):
        mapping = DirectMqttMapping.for_module(
            SimpleInOut, "prefix", "module", type_topic="values", autoclear=True
        )
        model = _simple_model(1.0)
        topic = next(iter(mapping.subscribe_topics()))
        mapping.handle_message(topic, model.model_dump_json(by_alias=True))
        assert mapping.result() == model
        assert mapping.result() is None

    async def test_wait_for_consumes_on_match(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data", autoclear=True)
        model = _simple_model(1.0)
        mapping.handle_message("sensors/data", model.model_dump_json(by_alias=True))
        assert await mapping.wait_for(lambda v: v == model, timeout_s=1.0) == model
        assert mapping.result() is None

    async def test_wait_for_preserves_non_matching(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data", autoclear=True)
        model = _simple_model(1.0)
        mapping.handle_message("sensors/data", model.model_dump_json(by_alias=True))
        with pytest.raises(TimeoutError):
            await mapping.wait_for(lambda v: v == _simple_model(2.0), timeout_s=0.05)
        assert mapping.result() == model

    async def test_wait_for_result_consumes(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data", autoclear=True)
        first = _simple_model(1.0)
        mapping.handle_message("sensors/data", first.model_dump_json(by_alias=True))
        assert await mapping.wait_for_result() == first
        assert mapping.result() is None
        second = _simple_model(2.0)
        mapping.handle_message("sensors/data", second.model_dump_json(by_alias=True))
        assert await mapping.wait_for_result() == second
        assert mapping.result() is None

    async def test_wait_for_result_without_autoclear_stays_sticky(self):
        mapping = DirectMqttMapping(SimpleInOut, "sensors/data")
        model = _simple_model(1.0)
        mapping.handle_message("sensors/data", model.model_dump_json(by_alias=True))
        assert await mapping.wait_for_result() == model
        assert mapping.result() == model


class TestControlChannelsAutoclear:
    def test_command_channels_consume(self, settings):
        listeners: list = []
        connector = mock.Mock()
        connector._register_listener.side_effect = listeners.append
        connector._create_publisher.side_effect = lambda _mapping, *args, **kwargs: (
            mock.AsyncMock()
        )
        description = ModuleDescription(
            SimpleInOut,
            SimpleInOut,
            SimpleParameters,
            lambda *_args, **_kwargs: mock.Mock(),
            SimpleMode,
            SimpleControllerState,
            mock.Mock,
        )
        channels = ControlChannels(connector, settings, "testmodule", description)

        def listener_for(fragment: str):
            return next(
                listener
                for listener in listeners
                if any(fragment in topic for topic in listener.subscribe_topics())
            )

        mode_listener = listener_for("automation-mode")
        mode_topic = next(iter(mode_listener.subscribe_topics()))
        mode_listener.handle_message(
            mode_topic, AutomationMode(mode="automatic").model_dump_json()
        )
        assert channels.get_automation_modes() == AutomationMode(mode="automatic")
        assert channels.get_automation_modes() is None

        parameters_listener = listener_for("parameters")
        parameters_topic = next(iter(parameters_listener.subscribe_topics()))
        parameters_listener.handle_message(
            parameters_topic, SimpleParameters().model_dump_json()
        )
        assert channels.get_parameters() == SimpleParameters()
        assert channels.get_parameters() is None

        manual_listener = listener_for("manual-values")
        manual_topic = next(iter(manual_listener.subscribe_topics()))
        manual_values = _simple_model(3.0)
        manual_listener.handle_message(
            manual_topic, manual_values.model_dump_json(by_alias=True)
        )
        assert channels.get_manual_controls() == manual_values
        assert channels.get_manual_controls() is None


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

        assert "/500000-thrs/module1/go-with-the" in topics
        assert topics[
            "/500000-thrs/module1/go-with-the"
        ] == flow_sensor.model_dump_json(by_alias=True)

    def test_subscribe_topic(self):
        clss = {"module1": SimpleInOut}
        mapping_no_suffix = ModuleMqttMapping(clss, PartialMqttMapping)

        assert mapping_no_suffix.subscribe_topics() == {"/500000-thrs/module1/+"}

    def test_builder(self):
        clss = {"module1": SimpleInOut}
        mapping = ModuleMqttMapping(clss, PartialMqttMapping)

        flow_sensor = FlowSensor(
            flow=Stamped.stamp(50.0), temperature=Stamped.stamp(5.0)
        )
        mapping.handle_message(
            "/500000-thrs/module1/go-with-the",
            flow_sensor.model_dump_json(by_alias=True),
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
        "devices_topic_prefix/500000-thrs/module/go-with-the/Command",
        "devices_topic_prefix/flow-topic/Command",
    }

    assert mock_mqtt_client.publish.call_args_list == [
        mock.call(
            "devices_topic_prefix/500000-thrs/module/go-with-the/Command",
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
            "devices_topic_prefix/500000-thrs/module/go-with-the/Command",
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
            "devices_topic_prefix/500000-thrs/module/go-with-the/Command",
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
    for payload, (flow, temperature) in zip(payloads, expected_values, strict=False):
        assert payload.flow.value == flow
        assert payload.temperature.value == temperature

    payload_json = [json.loads(call.args[1]) for call in calls]
    assert payload_json[0] == {
        "Flow": {"Value": 1, "TimeStamp": mock.ANY},
        "Temperature": {"Value": 2, "TimeStamp": mock.ANY},
        "Quantity": {
            "Value": 0.0,
            "TimeStamp": "1970-01-01T00:00:00Z",
        },
    }
    assert payload_json[1] == {
        "Flow": {"Value": 3, "TimeStamp": mock.ANY},
        "Temperature": {"Value": 4, "TimeStamp": mock.ANY},
        "Quantity": {"Value": 0.0, "TimeStamp": "1970-01-01T00:00:00Z"},
    }


class TestMergedModuleMqttMapping:
    def test_split_to_topics_merges_sensor_and_control_per_component(self):
        topics = merged_mapping().split_to_topics(
            (merged_sensor_values(), merged_control_values())
        )

        assert set(topics) == {
            "base/500000-thrs/module/pump",
            "base/500000-thrs/module/temperature",
            "base/500000-thrs/module/valve",
        }

        pump_payload = json.loads(topics["base/500000-thrs/module/pump"])
        # sensor keys merged with the actuated CC_ key on one topic
        assert pump_payload["CC_DutyPoint"]["Value"] == 0.4
        assert pump_payload["CC_OnOff"]["Value"] is True
        assert pump_payload["Flow"]["Value"] == 10.0
        assert pump_payload["Temperature"]["Value"] == 20.0
        assert "Quantity" in pump_payload

        # control-only components keep their actuated payload
        valve_payload = json.loads(topics["base/500000-thrs/module/valve"])
        assert valve_payload == {"CC_Setpoint": mock.ANY}
        # sensor-only components keep their plain payload
        temperature_payload = json.loads(topics["base/500000-thrs/module/temperature"])
        assert set(temperature_payload) == {"Temperature"}

    def test_split_to_topics_handles_absent_sides(self):
        sensor_only = merged_mapping().split_to_topics((merged_sensor_values(), None))
        assert sensor_only == {}

        control_only = merged_mapping().split_to_topics((None, merged_control_values()))
        assert control_only == {}
