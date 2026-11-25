import json
import logging
from asyncio import TaskGroup
from collections import defaultdict
from collections.abc import Awaitable, Callable, Coroutine, Iterable, Mapping
from functools import partial
from typing import (
    Protocol,
    cast,
)

from aiomqtt import Client
from pydantic import TypeAdapter
from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.control.state import AutomationMode
from thrs.input_output.base import CombinedValues, ThrsValues, get_topic
from thrs.input_output.definitions.wire_context import (
    AMCS_RECEIVE_CONTEXT,
    AMCS_WRITE_CONTEXT,
    WireContext,
)
from thrs.input_output.model_builder import PartialModelBuilder
from thrs.orchestration.config import Config
from thrs.orchestration.module import ModuleClassMap, ModuleDescription
from thrs.runtime.messages import (
    SimulationStatusMessage,
    SimulationStatusSetMessage,
)
from thrs.utils.string import hyphenize

logger = logging.getLogger(__name__)

DEVICE_NAMESPACE = "500000-thrs"
SIMULATION_INPUTS_TOPIC = "simulation-inputs"
SIMULATION_OUTPUTS_TOPIC = "simulation-outputs"
# Each publish fans out to one message per topic, so a single simulation tick
# has ~350 publishes in flight; aiomqtt's default of 10 warns on every tick.
PENDING_PUBLISHES_WARNING_THRESHOLD = 1000


def device_module_prefix(module_name: str) -> str:
    return f"{DEVICE_NAMESPACE}/{module_name}"


class MqttReceiveMapping[M](Protocol):
    """Mapping between a model and MQTT topics to receive messages"""

    def subscribe_topics(self) -> set[str]: ...

    def receive_topics(self) -> set[str]: ...

    def handle_message(self, topic: str, json: str | bytes): ...

    def result(self) -> M | None: ...


class MqttSendMapping[M](Protocol):
    """Mapping between a model and MQTT topics to send messages"""

    def split_to_topics(self, model: M) -> dict[str, str]: ...


class MqttMapping[M](MqttReceiveMapping[M], MqttSendMapping[M]):
    """Mapping between a model and MQTT topics to send and receive messages"""


class MappingForModule[M](Protocol):
    def __call__(
        self,
        message_type: type[M],
        topic_prefix: str,
        module_name: str,
        topic_suffix: str | None = None,
        *,
        initial: M | None = None,
    ) -> MqttMapping[M]: ...


def _mappings_by_topic[R: MqttReceiveMapping](
    mappings: Iterable[R],
) -> dict[str, list[R]]:
    mappings_by_topic: defaultdict[str, list[R]] = defaultdict(list)
    for mapping in mappings:
        for topic in mapping.receive_topics():
            mappings_by_topic[topic].append(mapping)
    return dict(mappings_by_topic)


class PartialMqttMapping[M: ThrsValues](MqttMapping[M]):
    """
    MQTT mapping that maps each component in the model to a separate topic.

    Those topics can either be part of a specific topic base or can be configured to be entirely different.
    """

    def __init__(
        self,
        message_type: type[M],
        topic_prefix: str,
        module_name: str,
        topic_suffix: str | None = None,
        *,
        only_computed_fields: bool = False,
        context: WireContext | None = None,
        initial: M | None = None,
    ):
        """Given an `initial` model, the result starts from it and each received
        topic overrides its own component."""
        self._cls = message_type
        self._topic_prefix = topic_prefix
        self._module_prefix = module_name
        self._topic_suffix_str = f"/{topic_suffix}" if topic_suffix else ""
        self._only_computed_fields = only_computed_fields
        self._context = context
        self._subscribe_topics = {
            self._topic("+", field): field_name
            for field_name, field in message_type.model_fields.items()
        }
        self._topic_to_field = {
            self._topic(field_name, field): field_name
            for field_name, field in message_type.model_fields.items()
        }
        self._builder = PartialModelBuilder(self._cls, context, initial)

    @staticmethod
    def only_computed_fields[T: ThrsValues](
        message_type: type[T],
        topic_prefix: str,
        module_name: str,
        topic_suffix: str | None = None,
    ) -> PartialMqttMapping[T]:
        return PartialMqttMapping(
            message_type,
            topic_prefix,
            module_name,
            topic_suffix,
            only_computed_fields=True,
        )

    def split_to_topics(self, model: M) -> dict[str, str]:
        """A `None` component sends an empty payload, which clears its topic."""
        fields = (
            self._cls.model_computed_fields
            if self._only_computed_fields
            else self._cls.model_fields
        )
        return {
            self._topic(key, field): (
                ""
                if (component := getattr(model, key)) is None
                else component.model_dump_json(by_alias=True, context=self._context)
            )
            for key, field in fields.items()
        }

    def _topic(self, key: str, field: FieldInfo | ComputedFieldInfo) -> str:
        return f"{self._topic_prefix}/{(get_topic(field) or f'{self._module_prefix}/{hyphenize(key)}')}{self._topic_suffix_str}"

    def subscribe_topics(self) -> set[str]:
        return set(self._subscribe_topics.keys())

    def receive_topics(self) -> set[str]:
        return set(self._topic_to_field.keys())

    def handle_message(self, topic: str, json: str | bytes):
        if topic not in self._topic_to_field:
            return

        self._builder.input(self._topic_to_field[topic], json)

    def result(self) -> M | None:
        return self._builder.result()

    def on_complete(self, hook: Callable[[M], object]) -> None:
        self._builder.on_complete(hook)


class DirectMqttMapping[M: ThrsValues](
    MqttReceiveMapping[M], MqttSendMapping[M | None]
):
    """MQTT mapping that maps the entire model to a single topic"""

    def __init__(
        self,
        cls: type[M],
        topic: str,
        topic_suffix: str | None = None,
        *,
        autoclear: bool = False,
        context: WireContext | None = None,
    ):
        self._context = context
        self._cls = cls
        self._adapter: TypeAdapter[M] = TypeAdapter(cls)
        self._topic = f"{topic}{f'/{topic_suffix}' if topic_suffix else ''}"
        self._value = None
        self._hooks: list[Callable[[M], None]] = []
        self._autoclear = autoclear

    @staticmethod
    def for_module(
        message_type: type[M],
        topic_prefix: str,
        module_name: str,
        *,
        type_topic: str | None = None,
        topic_suffix: str | None = None,
        autoclear: bool = False,
        context: WireContext | None = None,
    ) -> DirectMqttMapping[M]:
        base = f"{topic_prefix}/{module_name}{f'/{type_topic}' if type_topic else ''}"
        return DirectMqttMapping(
            message_type,
            f"{base}{f'/{topic_suffix}' if topic_suffix else ''}",
            autoclear=autoclear,
            context=context,
        )

    def split_to_topics(self, model: M | None) -> dict[str, str]:
        """`None` sends an empty payload, which clears the topic."""
        payload = "" if model is None else model.model_dump_json(by_alias=True)
        return {self._topic: payload}

    def subscribe_topics(self) -> set[str]:
        return {self._topic}

    def receive_topics(self) -> set[str]:
        return {self._topic}

    def handle_message(self, topic: str, json: str | bytes):
        if topic == self._topic:
            self._value = self._adapter.validate_json(json, context=self._context)
            for hook in self._hooks:
                hook(self._value)

    def result(self) -> M | None:
        value = self._value
        if value is not None and self._autoclear:
            self._value = None
        return value

    def add_hook(self, hook: Callable[[M], None]):
        """`hook` runs synchronously for every message, so it can't be lost to
        scheduling; one that needs to await should only queue the work."""
        self._hooks.append(hook)


class ModuleMqttMapping[T: CombinedValues](MqttReceiveMapping[T]):
    """
    MQTT mapping for modules

    Accepts a `ModuleClassMap` instead of a single class.
    Delegates to `sub_mapping` for each sub-model, starting each from its model in
    `initial` if given.
    """

    def __init__(
        self,
        clss: ModuleClassMap,
        sub_mapping: MappingForModule,
        topic_prefix: str = "",
        topic_suffix: str | None = None,
        allow_incomplete: bool = False,
        initial: CombinedValues | None = None,
    ):
        self._topic_prefix = topic_prefix
        self._mappings: Mapping[str, MqttMapping[ThrsValues]] = {
            name: sub_mapping(
                module_cls,
                topic_prefix,
                device_module_prefix(name),
                topic_suffix,
                initial=None if initial is None else initial.values[name],
            )
            for name, module_cls in clss.items()
        }
        self._mappings_by_topic = _mappings_by_topic(self._mappings.values())
        self._allow_incomplete = allow_incomplete

    def split_to_topics(self, model: T) -> dict[str, str]:
        return {
            topic: value
            for module, model in model.values.items()
            for topic, value in self._mappings[module].split_to_topics(model).items()
        }

    def subscribe_topics(self) -> set[str]:
        return {
            topic
            for mapping in self._mappings.values()
            for topic in mapping.subscribe_topics()
        }

    def receive_topics(self) -> set[str]:
        return set(self._mappings_by_topic.keys())

    def handle_message(self, topic: str, json: str | bytes):
        for mapping in self._mappings_by_topic.get(topic, []):
            mapping.handle_message(topic, json)

    def result(self) -> T | None:
        mapping_result: dict[str, ThrsValues] = {
            module: result
            for module, mapping in self._mappings.items()
            if (result := mapping.result()) and result is not None
        }
        if self._allow_incomplete or set(mapping_result.keys()) == set(
            self._mappings.keys()
        ):
            return cast(T, CombinedValues(values=mapping_result))
        return None


class MergedModuleMqttMapping(MqttSendMapping[tuple[CombinedValues, CombinedValues]]):
    """Publish-only mapping that merges sensor values and actuated control
    values into a single JSON payload per component topic. (like the AMCS does)
    """

    def __init__(
        self,
        sensor_values_clss: ModuleClassMap,
        control_values_clss: ModuleClassMap,
        topic_prefix: str,
    ):
        self._sensor_values_mapping = ModuleMqttMapping(
            sensor_values_clss, PartialMqttMapping, topic_prefix
        )
        self._control_values_mapping = ModuleMqttMapping(
            control_values_clss,
            partial(PartialMqttMapping, context=AMCS_RECEIVE_CONTEXT),
            topic_prefix,
        )

    def split_to_topics(
        self, model: tuple[CombinedValues, CombinedValues]
    ) -> dict[str, str]:
        sensor_values, control_values = model
        merged: dict[str, dict[str, object]] = defaultdict(dict)
        self._merge_payloads(merged, sensor_values, self._sensor_values_mapping)
        self._merge_payloads(merged, control_values, self._control_values_mapping)
        return {topic: json.dumps(payload) for topic, payload in merged.items()}

    def _merge_payloads(
        self,
        merged: dict[str, dict[str, object]],
        values: CombinedValues,
        mapping: ModuleMqttMapping,
    ) -> None:
        for topic, payload in mapping.split_to_topics(values).items():
            merged[topic].update(json.loads(payload))


class ControlChannels[
    S: ThrsValues,
    C: ThrsValues,
    P: ThrsValues,
    M: ThrsValues,
    CS: ThrsValues,
]:
    def __init__(
        self,
        connector: MqttConnector,
        config: Config,
        module_name: str,
        control_module: ModuleDescription[S, C, P, M, CS],
        publish_qos: int = 1,
    ) -> None:

        sensor_values_mapping = PartialMqttMapping[S](
            control_module.sensor_values_cls,
            config.mqtt_devices_topic_prefix,
            device_module_prefix(module_name),
        )
        connector._register_listener(sensor_values_mapping)

        parameters_mapping = DirectMqttMapping[P].for_module(
            control_module.parameters_cls,
            config.mqtt_controller_topic_prefix,
            module_name,
            type_topic="parameters",
            topic_suffix=config.mqtt_controller_topic_suffix,
            autoclear=True,
            context=WireContext.SET,
        )
        connector._register_listener(parameters_mapping)

        manual_mode_mapping = DirectMqttMapping[AutomationMode].for_module(
            AutomationMode,
            config.mqtt_controller_topic_prefix,
            module_name,
            type_topic="automation-mode",
            topic_suffix=config.mqtt_controller_topic_suffix,
            autoclear=True,
            context=WireContext.SET,
        )
        connector._register_listener(manual_mode_mapping)
        manual_controls_mapping = DirectMqttMapping[C].for_module(
            control_module.control_values_cls,
            config.mqtt_controller_topic_prefix,
            module_name,
            type_topic="manual-values",
            topic_suffix=config.mqtt_controller_topic_suffix,
            autoclear=True,
            context=WireContext.SET,
        )
        connector._register_listener(manual_controls_mapping)
        # Writes the manual controls too, but its state is what the AMCS actuated, so
        # the MQTT GraphQL API confirms such a write once it is carried out.
        control_values_set_mapping = DirectMqttMapping[C].for_module(
            control_module.control_values_cls,
            config.mqtt_controller_topic_prefix,
            module_name,
            type_topic="control-values",
            topic_suffix=config.mqtt_controller_topic_suffix,
            autoclear=True,
            context=WireContext.SET,
        )
        connector._register_listener(control_values_set_mapping)

        self.send_control_values = connector._create_publisher(
            PartialMqttMapping[C](
                control_module.control_values_cls,
                config.mqtt_devices_topic_prefix,
                device_module_prefix(module_name),
                config.mqtt_control_topic_suffix,
                context=AMCS_WRITE_CONTEXT,
            ),
            qos=publish_qos,
        )
        actuated_control_values_mapping = PartialMqttMapping[C](
            control_module.control_values_cls,
            config.mqtt_devices_topic_prefix,
            device_module_prefix(module_name),
            context=AMCS_RECEIVE_CONTEXT,
        )
        connector._register_listener(actuated_control_values_mapping)
        self.send_computed_values = connector._create_publisher(
            PartialMqttMapping[S](
                control_module.sensor_values_cls,
                config.mqtt_controller_topic_prefix,
                module_name,
                only_computed_fields=True,
            ),
            qos=publish_qos,
        )
        self.send_controller_state = connector._create_publisher(
            PartialMqttMapping[CS](
                control_module.controller_state_cls,
                config.mqtt_controller_topic_prefix,
                module_name,
            ),
            qos=publish_qos,
        )
        self.send_actuated_control_values = connector._create_publisher(
            DirectMqttMapping[C].for_module(
                control_module.control_values_cls,
                config.mqtt_controller_topic_prefix,
                module_name,
                type_topic="control-values",
            ),
            qos=publish_qos,
        )

        self.get_sensor_values = sensor_values_mapping.result
        self.get_parameters = parameters_mapping.result
        self.get_automation_modes = manual_mode_mapping.result
        self.get_manual_controls = manual_controls_mapping.result
        self.get_control_values_set = control_values_set_mapping.result
        self.get_actuated_control_values = actuated_control_values_mapping.result
        self.on_first_actuated_control_values = (
            actuated_control_values_mapping.on_complete
        )


class SimulationChannels[
    I: ThrsValues,
    O: ThrsValues,
]:
    def __init__(
        self,
        connector: MqttConnector,
        config: Config,
        sensor_values_clss: ModuleClassMap,
        control_values_clss: ModuleClassMap,
        simulation_inputs_cls: type[I],
        simulation_outputs_cls: type[O],
        initial_control_values: CombinedValues,
    ) -> None:
        """Until control sends them, the control values are the initial ones, so the
        simulation need not wait for control, like the plant."""
        simulation_inputs_topic = (
            f"{config.mqtt_simulator_topic_prefix}/{SIMULATION_INPUTS_TOPIC}"
        )
        simulation_outputs_topic = (
            f"{config.mqtt_simulator_topic_prefix}/{SIMULATION_OUTPUTS_TOPIC}"
        )

        control_values_mapping = ModuleMqttMapping(
            control_values_clss,
            PartialMqttMapping,
            config.mqtt_devices_topic_prefix,
            config.mqtt_control_topic_suffix,
            initial=initial_control_values,
        )
        connector._register_listener(control_values_mapping)
        simulation_inputs_mapping = DirectMqttMapping(
            simulation_inputs_cls,
            simulation_inputs_topic,
            config.mqtt_simulator_topic_suffix,
            context=WireContext.SET,
        )
        connector._register_listener(simulation_inputs_mapping)

        self._merged_mapping = MergedModuleMqttMapping(
            sensor_values_clss,
            control_values_clss,
            config.mqtt_devices_topic_prefix,
        )
        # Every tick overwrites these values, so a lost message is harmless
        self._publish_merged = connector._create_publisher(self._merged_mapping, qos=0)
        self.send_simulation_inputs = connector._create_publisher(
            DirectMqttMapping(simulation_inputs_cls, simulation_inputs_topic), qos=0
        )
        self.send_simulation_outputs = connector._create_publisher(
            DirectMqttMapping(simulation_outputs_cls, simulation_outputs_topic),
            qos=0,
        )

        self.get_control_values = control_values_mapping.result
        self.get_simulation_inputs = simulation_inputs_mapping.result

    async def send_device_values(
        self, sensor_values: CombinedValues, control_values: CombinedValues
    ) -> None:
        await self._publish_merged((sensor_values, control_values))


class DirectivesChannels:
    def __init__(self, connector: MqttConnector, config: Config) -> None:
        status_set_mapping = DirectMqttMapping(
            SimulationStatusSetMessage,
            f"{config.mqtt_simulator_topic_prefix}/{SimulationStatusSetMessage.subscribe_topic()}",
            context=WireContext.SET,
        )
        connector._register_listener(status_set_mapping)

        status_topic = f"{config.mqtt_simulator_topic_prefix}/{SimulationStatusMessage.subscribe_topic()}"

        self.send_simulation_status = connector._create_publisher(
            DirectMqttMapping(SimulationStatusMessage, status_topic), retain=True
        )

        self.on_status_set = status_set_mapping.add_hook


class MqttConnector:
    def __init__(self, mqtt_client: Client):
        mqtt_client.pending_calls_threshold = PENDING_PUBLISHES_WARNING_THRESHOLD
        self._mqtt_client = mqtt_client
        self._listeners: list[MqttReceiveMapping[object]] = []
        self._started = False

    def _register_listener[T](self, receiver: MqttReceiveMapping[T]) -> None:
        if self._started:
            raise Exception("Can't register listeners after start")

        self._listeners.append(receiver)

    def _create_publisher[T](
        self, sender: MqttSendMapping[T], qos: int = 1, retain: bool = False
    ) -> Callable[[T], Awaitable[None]]:
        async def _publish(value: T):
            await self._publish_by_mapping(sender, value, qos=qos, retain=retain)

        return _publish

    async def _listen(self):
        listeners_by_topic = _mappings_by_topic(self._listeners)
        async for message in self._mqtt_client.messages:
            if message.payload != b"":
                for mapping in listeners_by_topic.get(message.topic.value, []):
                    if not isinstance(message.payload, str | bytes):
                        raise ValueError(
                            f"Expected string or bytes, got {type(message.payload)}"
                        )
                    try:
                        mapping.handle_message(message.topic.value, message.payload)
                    except Exception:
                        logger.exception(
                            "Failed handling MQTT message, message ignored"
                        )

    async def _publish_by_mapping[T](
        self, mapping: MqttSendMapping[T], value: T, qos: int, retain: bool
    ):
        payloads = mapping.split_to_topics(value)
        async with TaskGroup() as tg:
            for topic, payload in payloads.items():
                logging.debug("Publishing on %s", topic)
                tg.create_task(
                    self._mqtt_client.publish(topic, payload, qos=qos, retain=retain)
                )

    async def _start(self):
        for mapping in self._listeners:
            for topic in mapping.subscribe_topics():
                await self._mqtt_client.subscribe(topic, qos=1)

    async def run(self) -> Coroutine[None, None, None]:
        await self._start()
        self._started = True
        return self._listen()
