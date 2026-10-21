from __future__ import annotations

from dataclasses import dataclass
from types import NoneType, UnionType
from typing import Annotated, Any, Literal, Union, get_args, get_origin

from more_itertools import one
from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.input_output.base import ComponentType, ThrsValues, get_component_type
from thrs.orchestration.comms import (
    ControlChannels,
    DirectivesChannels,
    DirectMqttMapping,
    MergedModuleMqttMapping,
    ModuleMqttMapping,
    MqttConnector,
    MqttReceiveMapping,
    MqttSendMapping,
    PartialMqttMapping,
    SimulationChannels,
)
from thrs.orchestration.config import Config
from thrs.runtime.descriptions.simulation import Mode

Direction = Literal["send", "receive"]


@dataclass
class TopicMapping:
    topic: str
    payload_type: type[ThrsValues]
    direction: Direction
    component_type: ComponentType
    qos: int | None = None
    retain: bool = False


def _strip_none(annotation: Any) -> Any:
    if get_origin(annotation) == Annotated:
        annotation = get_args(annotation)[0]

    if get_origin(annotation) in (UnionType, Union):
        return one(a for a in get_args(annotation) if a is not NoneType)
    return annotation


def _field_annotation(field: FieldInfo | ComputedFieldInfo) -> type[ThrsValues]:
    raw = field.annotation if isinstance(field, FieldInfo) else field.return_type
    return _strip_none(raw)


def _describe_mapping(
    config: Config,
    mapping: MqttSendMapping[ThrsValues] | MqttReceiveMapping[ThrsValues],
) -> list[tuple[str, type[ThrsValues], ComponentType]]:
    """(topic, _type type) pairs from a mapping, using its own topic-building logic."""
    if isinstance(mapping, PartialMqttMapping):
        if mapping._topic_prefix == config.mqtt_devices_topic_prefix:
            return []

        fields = (
            mapping._cls.model_computed_fields
            if mapping._only_computed_fields
            else mapping._cls.model_fields
        )
        return [
            (
                mapping._topic(name, field),
                _field_annotation(field),
                get_component_type(field),
            )
            for name, field in fields.items()
        ]
    if isinstance(mapping, DirectMqttMapping):
        return [(mapping._topic, t, None) for t in mapping._types]
    if isinstance(mapping, ModuleMqttMapping):
        return [
            pair
            for sub in mapping._mappings.values()
            for pair in _describe_mapping(config, sub)
        ]
    if isinstance(mapping, MergedModuleMqttMapping):
        return []  # Only used for simulating amcs devices
    raise TypeError(
        f"Don't know how to describe {type(mapping)!r} for the AsyncAPI spec"
    )


async def _dummy_publish(_value):
    return None


class RecordingConnector(MqttConnector):
    """Fake MqttConnector that records what the *Channels constructors register."""

    def __init__(self, config) -> None:
        self.topics: list[TopicMapping] = []
        self._config = config

    def _register_listener(self, receiver: MqttReceiveMapping) -> None:
        for topic, payload, component_type in _describe_mapping(self._config, receiver):
            self.topics.append(TopicMapping(topic, payload, "receive", component_type))

    def _create_publisher(
        self, sender: MqttSendMapping, qos: int = 1, retain: bool = False
    ):
        for topic, payload, component_type in _describe_mapping(self._config, sender):
            self.topics.append(
                TopicMapping(topic, payload, "send", component_type, qos, retain)
            )

        return _dummy_publish


def collect_topics(config: Config, thrs_mode: Mode) -> list[TopicMapping]:
    modules = thrs_mode.control_modules
    simulation_description = thrs_mode.simulation_description

    if simulation_description is None:
        raise RuntimeError(
            'Mode "thrs" has no simulation description; cannot build the spec.'
        )

    connector = RecordingConnector(config)

    for module_name, description in modules.items():
        ControlChannels(connector, config, module_name, description)

    SimulationChannels(
        connector,
        config,
        {},  # The simulated devices are covered by other specs
        {},  # The simulated devices are covered by other specs
        type(simulation_description.simulation_inputs),
        simulation_description.simulation_outputs_cls,
    )
    DirectivesChannels(connector, config)

    return connector.topics
