import json
import logging
from asyncio import Event, Future, gather, timeout
from collections import defaultdict
from collections.abc import Awaitable, Callable, Coroutine, Mapping
from inspect import isawaitable
from typing import (
    Protocol,
    cast,
)

from aiomqtt import Client
from paho.mqtt.client import topic_matches_sub
from pydantic import TypeAdapter
from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.control.switching import AutomationMode, SwitchingControlMode
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
    PauseMessage,
    PlayMessage,
    SimulationStatusMessage,
    StepMessage,
)
from thrs.utils.string import hyphenize

logger = logging.getLogger(__name__)


class MqttReceiveMapping[M](Protocol):
    """Mapping between a model and MQTT topics to receive messages"""

    def subscribe_topics(self) -> set[str]: ...

    def handle_message(self, topic: str, json: str | bytes): ...

    def result(self) -> M | None: ...

    async def wait_for_result(self) -> M: ...


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
    ) -> MqttMapping[M]: ...


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
    ):
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
        self._builder = PartialModelBuilder(self._cls, context)
        self._update_event = Event()

    @staticmethod
    def only_computed_fields[T: ThrsValues](
        message_type: type[T],
        topic_prefix: str,
        module_name: str,
        topic_suffix: str | None = None,
    ) -> "PartialMqttMapping[T]":
        return PartialMqttMapping(
            message_type,
            topic_prefix,
            module_name,
            topic_suffix,
            only_computed_fields=True,
        )

    def split_to_topics(self, model: M) -> dict[str, str]:
        fields = (
            self._cls.model_computed_fields
            if self._only_computed_fields
            else self._cls.model_fields
        )
        return {
            self._topic(key, field): getattr(model, key).model_dump_json(
                by_alias=True, context=self._context
            )
            for key, field in fields.items()
        }

    def _topic(self, key: str, field: FieldInfo | ComputedFieldInfo) -> str:
        return f"{self._topic_prefix}/{(get_topic(field) or f'{self._module_prefix}/{hyphenize(key)}')}{self._topic_suffix_str}"

    def subscribe_topics(self) -> set[str]:
        return set(self._subscribe_topics.keys())

    def handle_message(self, topic: str, json: str | bytes):
        if topic not in self._topic_to_field:
            return

        self._builder.input(self._topic_to_field[topic], json)
        self._update_event.set()

    def result(self) -> M | None:
        return self._builder.result()

    async def wait_for_result(self) -> M:
        return await self._builder.wait_for_result()

    async def wait_for_update(self):
        await self._update_event.wait()
        self._update_event.clear()

    async def wait_for(self, condition: Callable[[M], bool], timeout_s: float) -> M:
        async with timeout(timeout_s):
            while True:
                if (result := self.result()) and condition(result):
                    return result
                await self.wait_for_update()


class DirectMqttMapping[M: ThrsValues](MqttMapping[M]):
    """MQTT mapping that maps the entire model to a single topic"""

    def __init__(
        self,
        cls: type[M] | tuple[type[M], ...],
        topic: str,
        topic_suffix: str | None = None,
    ):
        self._types = cls if isinstance(cls, tuple) else (cls,)
        validate_type: type[M] | object = self._types[0]
        for extra_type in self._types[1:]:
            validate_type = validate_type | extra_type
        self._adapter: TypeAdapter[M] = TypeAdapter(validate_type)
        self._topic = f"{topic}{f'/{topic_suffix}' if topic_suffix else ''}"
        self._value = None
        self._future = Future()
        self._update_event = Event()
        self._hooks: list[Callable[[M], object]] = []

    @staticmethod
    def for_module(
        message_type: type[M],
        topic_prefix: str,
        module_name: str,
        *,
        type_topic: str | None = None,
        topic_suffix: str | None = None,
    ) -> "DirectMqttMapping[M]":
        base = f"{topic_prefix}/{module_name}{f'/{type_topic}' if type_topic else ''}"
        return DirectMqttMapping(
            message_type,
            f"{base}{f'/{topic_suffix}' if topic_suffix else ''}",
        )

    def split_to_topics(self, model: M) -> dict[str, str]:
        return {self._topic: model.model_dump_json(by_alias=True)}

    def subscribe_topics(self) -> set[str]:
        return {self._topic}

    def handle_message(self, topic: str, json: str | bytes):
        awaitables: list[Awaitable] = []
        if topic == self._topic:
            self._value = cast(M, self._adapter.validate_json(json))
            if not self._future.done():
                self._future.set_result(self._value)
            self._update_event.set()
            for hook in self._hooks:
                result = hook(self._value)
                if isawaitable(result):
                    awaitables.append(result)
        gather(*awaitables, return_exceptions=True)

    def result(self) -> M | None:
        return self._value

    async def wait_for_result(self) -> M:
        return await self._future

    async def wait_for_update(self):
        await self._update_event.wait()
        self._update_event.clear()

    async def wait_for(self, condition: Callable[[M], bool], timeout_s: float) -> M:
        async with timeout(timeout_s):
            while True:
                if (result := self.result()) and condition(result):
                    return result
                await self.wait_for_update()

    def add_hook(self, hook: Callable[[M], object]):
        self._hooks.append(hook)


class ModuleMqttMapping[T: CombinedValues](MqttReceiveMapping[T]):
    """
    MQTT mapping for modules

    Accepts a `ModuleClassMap` instead of a single class.
    Delegates to `sub_mapping` for each sub-model.
    """

    def __init__(
        self,
        clss: ModuleClassMap,
        sub_mapping: MappingForModule,
        topic_prefix: str = "",
        topic_suffix: str | None = None,
        allow_incomplete: bool = False,
    ):
        self._topic_prefix = topic_prefix
        self._mappings: Mapping[str, MqttMapping[ThrsValues]] = {
            name: sub_mapping(
                module_cls,
                topic_prefix,
                f"500000-thrs/{name}",
                topic_suffix,
            )
            for name, module_cls in clss.items()
        }
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

    def handle_message(self, topic: str, json: str | bytes):
        for mapping in self._mappings.values():
            if any(
                topic_matches_sub(subscribed_topic, topic)
                for subscribed_topic in mapping.subscribe_topics()
            ):
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

    async def wait_for_result(self) -> T:
        results = await gather(
            *(builder.wait_for_result() for builder in self._mappings.values())
        )
        return cast(
            T, CombinedValues(dict(zip(self._mappings.keys(), results, strict=False)))
        )


class MergedModuleMqttMapping(
    MqttSendMapping[tuple[CombinedValues | None, CombinedValues | None]]
):
    """Publish-only mapping that merges sensor values and actuated control
    values into a single JSON payload per component topic. (like the AMCS does)
    """

    def __init__(
        self,
        sensor_values_clss: ModuleClassMap,
        control_values_clss: ModuleClassMap,
        topic_prefix: str,
    ):
        self._sensor_values: CombinedValues | None = None
        self._control_values: CombinedValues | None = None
        self._sensor_values_mappings = {
            name: PartialMqttMapping(cls, topic_prefix, f"500000-thrs/{name}")
            for name, cls in sensor_values_clss.items()
        }
        self._control_values_mappings = {
            name: PartialMqttMapping(
                cls,
                topic_prefix,
                f"500000-thrs/{name}",
                context=AMCS_RECEIVE_CONTEXT,
            )
            for name, cls in control_values_clss.items()
        }

    def split_to_topics(
        self, model: tuple[CombinedValues | None, CombinedValues | None]
    ) -> dict[str, str]:
        sensor_values, control_values = model
        self._sensor_values = sensor_values or self._sensor_values
        self._control_values = control_values or self._control_values
        if self._sensor_values is None or self._control_values is None:
            return {}
        merged: dict[str, dict[str, object]] = defaultdict(dict)
        self._merge_payloads(merged, self._sensor_values, self._sensor_values_mappings)
        self._merge_payloads(
            merged, self._control_values, self._control_values_mappings
        )
        return {topic: json.dumps(payload) for topic, payload in merged.items()}

    def _merge_payloads(
        self,
        merged: dict[str, dict[str, object]],
        values: CombinedValues,
        mappings: Mapping[str, PartialMqttMapping],
    ) -> None:
        for module_name, mapping in mappings.items():
            module = values.values.get(module_name)
            if module is None:
                continue
            for topic, payload in mapping.split_to_topics(module).items():
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
        connector: "MqttConnector",
        config: Config,
        module_name: str,
        control_module: ModuleDescription[S, C, P, M, CS],
    ) -> None:
        sensor_values_mapping = PartialMqttMapping[S](
            control_module.sensor_values_cls,
            config.mqtt_devices_topic_prefix,
            f"500000-thrs/{module_name}",
        )
        connector._register_listener(sensor_values_mapping)

        parameters_mapping = DirectMqttMapping[P].for_module(
            control_module.parameters_cls,
            config.mqtt_controller_topic_prefix,
            module_name,
            type_topic="parameters",
            topic_suffix=config.mqtt_controller_topic_suffix,
        )
        connector._register_listener(parameters_mapping)

        manual_mode_mapping = DirectMqttMapping[AutomationMode].for_module(
            AutomationMode,
            config.mqtt_controller_topic_prefix,
            module_name,
            type_topic="automation-mode",
            topic_suffix=config.mqtt_controller_topic_suffix,
        )
        connector._register_listener(manual_mode_mapping)
        manual_controls_mapping = DirectMqttMapping[C].for_module(
            control_module.control_values_cls,
            config.mqtt_controller_topic_prefix,
            module_name,
            type_topic="manual-values",
            topic_suffix=config.mqtt_controller_topic_suffix,
        )
        connector._register_listener(manual_controls_mapping)

        self.send_control_values = connector._create_publisher(
            PartialMqttMapping[C](
                control_module.control_values_cls,
                config.mqtt_devices_topic_prefix,
                f"500000-thrs/{module_name}",
                config.mqtt_control_topic_suffix,
                context=AMCS_WRITE_CONTEXT,
            ),
        )
        actuated_control_values_mapping = PartialMqttMapping[C](
            control_module.control_values_cls,
            config.mqtt_devices_topic_prefix,
            f"500000-thrs/{module_name}",
            context=AMCS_RECEIVE_CONTEXT,
        )
        connector._register_listener(actuated_control_values_mapping)
        self.send_computed_values = connector._create_publisher(
            PartialMqttMapping[S](
                control_module.sensor_values_cls,
                config.mqtt_controller_topic_prefix,
                module_name,
                only_computed_fields=True,
            )
        )
        self.send_controller_state = connector._create_publisher(
            DirectMqttMapping[CS].for_module(
                control_module.controller_state_cls,
                config.mqtt_controller_topic_prefix,
                module_name,
                type_topic="controller-state",
            ),
        )
        self.send_parameters = connector._create_publisher(
            DirectMqttMapping[P].for_module(
                control_module.parameters_cls,
                config.mqtt_controller_topic_prefix,
                module_name,
                type_topic="parameters",
            )
        )
        self.send_control_modes = connector._create_publisher(
            DirectMqttMapping[M].for_module(
                control_module.control_mode_cls,
                config.mqtt_controller_topic_prefix,
                module_name,
                type_topic="control-mode",
            )
        )
        self.send_manual_control = connector._create_publisher(
            DirectMqttMapping[C].for_module(
                control_module.control_values_cls,
                config.mqtt_controller_topic_prefix,
                module_name,
                type_topic="manual-values",
            )
        )

        self.get_sensor_values = sensor_values_mapping.result
        self.get_parameters = parameters_mapping.result
        self.get_automation_modes = manual_mode_mapping.result
        self.get_manual_controls = manual_controls_mapping.result
        self.get_actuated_control_values = actuated_control_values_mapping.result


class SimulationChannels[
    I: ThrsValues,
    O: ThrsValues,
]:
    def __init__(
        self,
        connector: "MqttConnector",
        config: "Config",
        sensor_values_clss: ModuleClassMap,
        control_values_clss: ModuleClassMap,
        simulation_inputs_cls: type[I] | tuple[type[I], ...],
        simulation_outputs_cls: type[O] | tuple[type[O], ...],
    ) -> None:
        simulation_inputs_topic = (
            f"{config.mqtt_simulator_topic_prefix}/simulation-inputs"
        )
        simulation_outputs_topic = (
            f"{config.mqtt_simulator_topic_prefix}/simulation-outputs"
        )

        control_values_mapping = ModuleMqttMapping(
            control_values_clss,
            PartialMqttMapping,
            config.mqtt_devices_topic_prefix,
            config.mqtt_control_topic_suffix,
        )
        connector._register_listener(control_values_mapping)
        simulation_inputs_mapping = DirectMqttMapping(
            simulation_inputs_cls,
            simulation_inputs_topic,
            config.mqtt_simulator_topic_suffix,
        )
        connector._register_listener(simulation_inputs_mapping)

        self._merged_mapping = MergedModuleMqttMapping(
            sensor_values_clss,
            control_values_clss,
            config.mqtt_devices_topic_prefix,
        )
        self._publish_merged = connector._create_publisher(self._merged_mapping)
        self.send_simulation_inputs = connector._create_publisher(
            DirectMqttMapping(simulation_inputs_cls, simulation_inputs_topic)
        )
        self.send_simulation_outputs = connector._create_publisher(
            DirectMqttMapping(simulation_outputs_cls, simulation_outputs_topic),
        )

        self.get_control_values = control_values_mapping.result
        self.wait_for_control_values = control_values_mapping.wait_for_result
        self.get_simulation_inputs = simulation_inputs_mapping.result

    async def send_sensor_values(self, sensor_values: CombinedValues) -> None:
        await self._publish_merged((sensor_values, None))

    async def send_actuated_control_values(
        self, control_values: CombinedValues
    ) -> None:
        await self._publish_merged((None, control_values))


class ControlApiChannels[
    S: ThrsValues,
    C: ThrsValues,
    P: ThrsValues,
    M: ThrsValues,
    CS: ThrsValues,
]:
    def __init__(
        self,
        connector: "MqttConnector",
        config: "Config",
        module_name: str,
        module_description: "ModuleDescription[S, C, P, M, CS]",
    ) -> None:
        self.module_name = module_name
        sensor_values_mapping = PartialMqttMapping[S](
            module_description.sensor_values_cls,
            config.mqtt_devices_topic_prefix,
            f"500000-thrs/{module_name}",
        )
        connector._register_listener(sensor_values_mapping)

        actuated_control_values_mapping = PartialMqttMapping[C](
            module_description.control_values_cls,
            config.mqtt_devices_topic_prefix,
            f"500000-thrs/{module_name}",
            context=AMCS_RECEIVE_CONTEXT,
        )
        connector._register_listener(actuated_control_values_mapping)

        manual_values_mapping = DirectMqttMapping[C].for_module(
            module_description.control_values_cls,
            config.mqtt_controller_topic_prefix,
            module_name,
            type_topic="manual-values",
        )
        connector._register_listener(manual_values_mapping)

        # We should not need to wrap here with SwitchingControlMode because it exposes SwitchingControlMode
        # which we should not have to know about here... This needs a refactor of how switching control is handled
        control_modes_mapping = DirectMqttMapping[SwitchingControlMode[M]].for_module(
            SwitchingControlMode[module_description.control_mode_cls],
            config.mqtt_controller_topic_prefix,
            module_name,
            type_topic="control-mode",
        )
        connector._register_listener(control_modes_mapping)

        parameters_mapping = DirectMqttMapping[P].for_module(
            module_description.parameters_cls,
            config.mqtt_controller_topic_prefix,
            module_name,
            type_topic="parameters",
        )
        connector._register_listener(parameters_mapping)

        controller_state_mapping = DirectMqttMapping[CS].for_module(
            module_description.controller_state_cls,
            config.mqtt_controller_topic_prefix,
            module_name,
            type_topic="controller-state",
        )
        connector._register_listener(controller_state_mapping)

        self.send_manual_values = connector._create_publisher(
            DirectMqttMapping[C].for_module(
                module_description.control_values_cls,
                config.mqtt_controller_topic_prefix,
                module_name,
                type_topic="manual-values",
                topic_suffix=config.mqtt_controller_topic_suffix,
            )
        )
        self.send_automation_mode = connector._create_publisher(
            DirectMqttMapping[AutomationMode].for_module(
                AutomationMode,
                config.mqtt_controller_topic_prefix,
                module_name,
                type_topic="automation-mode",
                topic_suffix=config.mqtt_controller_topic_suffix,
            )
        )
        self.send_parameters = connector._create_publisher(
            DirectMqttMapping[P].for_module(
                module_description.parameters_cls,
                config.mqtt_controller_topic_prefix,
                module_name,
                type_topic="parameters",
                topic_suffix=config.mqtt_controller_topic_suffix,
            )
        )

        self.get_sensor_values = sensor_values_mapping.result
        self.get_actuated_control_values = actuated_control_values_mapping.result
        self.get_manual_values = manual_values_mapping.result
        self.get_control_modes = control_modes_mapping.result
        self.get_parameters = parameters_mapping.result
        self.get_controller_state = controller_state_mapping.result
        self.wait_for_manual_values = manual_values_mapping.wait_for
        self.wait_for_parameters = parameters_mapping.wait_for
        self.wait_for_control_modes = control_modes_mapping.wait_for


class SimulationApiChannels[I: ThrsValues, O: ThrsValues]:
    def __init__(
        self,
        connector: "MqttConnector",
        config: "Config",
        simulation_inputs_cls: type[I] | tuple[type[I], ...],
        simulation_outputs_cls: type[O] | tuple[type[O], ...],
    ) -> None:
        self.simulation_inputs_mapping = DirectMqttMapping(
            simulation_inputs_cls,
            f"{config.mqtt_simulator_topic_prefix}/simulation-inputs",
        )
        connector._register_listener(self.simulation_inputs_mapping)

        self.simulation_outputs_mapping = DirectMqttMapping(
            simulation_outputs_cls,
            f"{config.mqtt_simulator_topic_prefix}/simulation-outputs",
        )
        connector._register_listener(self.simulation_outputs_mapping)

        self.send_simulation_inputs = connector._create_publisher(
            DirectMqttMapping(
                simulation_inputs_cls,
                f"{config.mqtt_simulator_topic_prefix}/simulation-inputs/{config.mqtt_simulator_topic_suffix}",
            )
        )

        self.get_simulation_inputs = self.simulation_inputs_mapping.result
        self.get_simulation_outputs = self.simulation_outputs_mapping.result
        self.wait_for_simulation_inputs = self.simulation_inputs_mapping.wait_for


class DirectivesChannels:
    def __init__(self, connector: "MqttConnector", config: "Config") -> None:
        self._connector = connector
        play_mapping = DirectMqttMapping(
            PlayMessage,
            f"{config.mqtt_simulator_topic_prefix}/{PlayMessage.subscribe_topic()}",
        )
        connector._register_listener(play_mapping)

        step_mapping = DirectMqttMapping(
            StepMessage,
            f"{config.mqtt_simulator_topic_prefix}/{StepMessage.subscribe_topic()}",
        )
        connector._register_listener(step_mapping)

        pause_mapping = DirectMqttMapping(
            PauseMessage,
            f"{config.mqtt_simulator_topic_prefix}/{PauseMessage.subscribe_topic()}",
        )
        connector._register_listener(pause_mapping)

        self._status_topic = f"{config.mqtt_simulator_topic_prefix}/{SimulationStatusMessage.subscribe_topic()}"

        self.send_simulation_status = connector._create_publisher(
            DirectMqttMapping(SimulationStatusMessage, self._status_topic), retain=True
        )

        self.on_play = play_mapping.add_hook
        self.on_step = step_mapping.add_hook
        self.on_pause = pause_mapping.add_hook

    async def clear_simulation_status(self):
        await self._connector._mqtt_client.publish(
            self._status_topic, b"", qos=1, retain=True
        )


class DirectivesApiChannels:
    def __init__(self, connector: "MqttConnector", config: "Config") -> None:
        status_topic = f"{config.mqtt_simulator_topic_prefix}/{SimulationStatusMessage.subscribe_topic()}"
        simulation_status_mapping = DirectMqttMapping(
            SimulationStatusMessage, status_topic
        )
        connector._register_listener(simulation_status_mapping)

        self._send_play = connector._create_publisher(
            DirectMqttMapping(
                PlayMessage,
                f"{config.mqtt_simulator_topic_prefix}/{PlayMessage.subscribe_topic()}",
            )
        )
        self._send_step = connector._create_publisher(
            DirectMqttMapping(
                StepMessage,
                f"{config.mqtt_simulator_topic_prefix}/{StepMessage.subscribe_topic()}",
            )
        )
        self._send_pause = connector._create_publisher(
            DirectMqttMapping(
                PauseMessage,
                f"{config.mqtt_simulator_topic_prefix}/{PauseMessage.subscribe_topic()}",
            )
        )

        self.get_simulation_status = simulation_status_mapping.result
        self.wait_for_simulation_status = simulation_status_mapping.wait_for_result
        self.wait_for_simulation_status_where = simulation_status_mapping.wait_for
        self.on_simulation_status = simulation_status_mapping.add_hook

    async def send_play(self, playback_rate: float):
        await self._send_play(PlayMessage(playback_rate=playback_rate))

    async def send_step(self, seconds: float):
        await self._send_step(StepMessage(seconds=seconds))

    async def send_pause(self):
        await self._send_pause(PauseMessage())


class MqttConnector:
    def __init__(self, mqtt_client: Client):
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
        async for message in self._mqtt_client.messages:
            if message.payload != b"":
                matching_mappings = [
                    mapping
                    for mapping in self._listeners
                    for topic in mapping.subscribe_topics()
                    if message.topic.matches(topic)
                ]
                for mapping in matching_mappings:
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
        for topic, payload in payloads.items():
            logging.debug("Publishing on %s", topic)
            await self._mqtt_client.publish(topic, payload, qos=qos, retain=retain)

    async def _start(self):
        for mapping in self._listeners:
            for topic in mapping.subscribe_topics():
                await self._mqtt_client.subscribe(topic, qos=1)

    async def run(self) -> Coroutine[None, None, None]:
        await self._start()
        self._started = True
        return self._listen()
