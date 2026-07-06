import logging
from asyncio import Event, Future, ensure_future, gather, timeout
from collections.abc import Mapping
from dataclasses import dataclass
from inspect import isawaitable
from typing import (
    Awaitable,
    Callable,
    Coroutine,
    Protocol,
    TypeVarTuple,
    Unpack,
    cast,
)

from aiomqtt import Client
from pydantic import TypeAdapter
from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.control.switching import AutomationMode, SwitchingControlMode
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
    get_topic,
)
from thrs.input_output.model_builder import PartialModelBuilder
from thrs.orchestration.config import Config
from thrs.orchestration.module import CombinedModule, ModuleClassMap, ModuleDescription
from thrs.orchestration.simulation import Simulation
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
    ):
        self._cls = message_type
        self._topic_prefix = topic_prefix
        self._module_prefix = module_name
        self._topic_suffix_str = f"/{topic_suffix}" if topic_suffix else ""
        self._only_computed_fields = only_computed_fields
        self._subscribe_topics = {
            self._topic("+", field): field_name
            for field_name, field in message_type.model_fields.items()
        }
        self._topic_to_field = {
            self._topic(field_name, field): field_name
            for field_name, field in message_type.model_fields.items()
        }
        self._builder = PartialModelBuilder(self._cls)
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
            self._topic(key, field): getattr(model, key).model_dump_json(by_alias=True)
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
        topic_suffix: str | None = None,
        *,
        type_topic: str | None = None,
    ) -> "DirectMqttMapping[M]":
        base = f"{topic_prefix}/{module_name}{f'/{type_topic}' if type_topic else ''}"
        return DirectMqttMapping(
            message_type,
            f"{base}{f'/{topic_suffix}' if topic_suffix else ''}",
        )

    @staticmethod
    def for_module_type(type_topic: str) -> "MappingForModule":
        def _fn(
            message_type,
            topic_prefix: str,
            module_name: str,
            topic_suffix: str | None = None,
        ) -> "DirectMqttMapping":
            return DirectMqttMapping.for_module(
                message_type,
                topic_prefix,
                module_name,
                topic_suffix,
                type_topic=type_topic,
            )

        return _fn  # type: ignore[return-value]

    def split_to_topics(self, model: M) -> dict[str, str]:
        return {self._topic: model.model_dump_json(by_alias=True)}

    def subscribe_topics(self) -> set[str]:
        return {self._topic}

    def handle_message(self, topic: str, json: str | bytes):
        if topic == self._topic:
            self._value = cast(M, self._adapter.validate_json(json))
            if not self._future.done():
                self._future.set_result(self._value)
            self._update_event.set()
            for hook in self._hooks:
                result = hook(self._value)
                if isawaitable(result):
                    ensure_future(result)

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
    Delegates to `PartialMqttMapping` for each sub-model.
    """

    def __init__(
        self,
        clss: ModuleClassMap,
        sub_mapping: MappingForModule,
        topic_prefix: str = "",
        topic_suffix: str | None = None,
        allow_incomplete: bool = False,
    ):
        self._clss = clss
        self._topic_prefix = topic_prefix
        self._mappings: Mapping[str, MqttMapping[ThrsValues]] = {
            name: sub_mapping(
                module_cls,
                topic_prefix,
                name,
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
            if topic in mapping.subscribe_topics():
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
        else:
            return None

    async def wait_for_result(self) -> T:
        results = await gather(
            *(builder.wait_for_result() for builder in self._mappings.values())
        )
        return cast(T, CombinedValues(dict(zip(self._mappings.keys(), results))))


type Publisher[T] = Callable[[T], Awaitable[None]]


class Channels[D, C](Protocol):
    @classmethod
    def _register(
        cls,
        connector: "MqttConnector",
        description: D,
    ) -> C: ...


Ts = TypeVarTuple("Ts")


class MqttConnectorBuilder[*Ts]:
    def __init__(
        self,
        connector: "MqttConnector",
        registrations: tuple[Callable[[], object], ...] = (),
    ):
        self._connector = connector
        self._registrations = registrations

    def add[D, C](
        self,
        channels_type: type[Channels[D, C]],
        description: D,
    ) -> "MqttConnectorBuilder[*Ts, C]":
        def _register() -> C:
            return channels_type._register(self._connector, description)

        return cast(
            MqttConnectorBuilder[*Ts, C],
            MqttConnectorBuilder(
                self._connector,
                (*self._registrations, _register),
            ),
        )

    def register(self) -> tuple[Unpack[Ts]]:
        return cast(
            tuple[Unpack[Ts]], tuple(register() for register in self._registrations)
        )

    async def run(self) -> tuple[tuple[Unpack[Ts]], Coroutine[None, None, None]]:
        channels = self.register()
        await self._connector._start()
        return cast(tuple[Unpack[Ts]], channels), self._connector._listen()


@dataclass
class ControlChannelsDescription:
    devices_topic_prefix: str
    controller_topic_prefix: str
    sensor_values_clss: ModuleClassMap
    control_values_clss: ModuleClassMap
    controller_state_clss: ModuleClassMap
    parameters_clss: ModuleClassMap
    control_modes_clss: ModuleClassMap
    control_values_topic_suffix: str
    controller_topic_suffix: str

    @staticmethod
    def from_settings(
        config: "Config", control_module: "CombinedModule"
    ) -> "ControlChannelsDescription":
        return ControlChannelsDescription(
            devices_topic_prefix=config.mqtt_devices_topic_prefix,
            controller_topic_prefix=config.mqtt_controller_topic_prefix,
            sensor_values_clss=control_module.sensor_values_clss,
            control_values_clss=control_module.control_values_clss,
            controller_state_clss=control_module.controller_state_clss,
            control_values_topic_suffix=config.mqtt_control_topic_suffix,
            control_modes_clss=control_module.control_modes_clss,
            parameters_clss=control_module.parameters_clss,
            controller_topic_suffix=config.mqtt_controller_topic_suffix,
        )


class ControlChannels[S: CombinedValues, P: CombinedValues](
    Channels[ControlChannelsDescription, "ControlChannels[S, P]"]
):
    def __init__(
        self,
        sensor_values_mapping: ModuleMqttMapping[S],
        send_control_values: Publisher[CombinedValues],
        send_computed_values: Publisher[CombinedValues],
        send_controller_state: Publisher[CombinedValues],
        parameters_mapping: ModuleMqttMapping[P],
        send_parameters: Publisher[CombinedValues],
        send_control_modes: Publisher[CombinedValues],
        send_manual_control: Publisher[CombinedValues],
        automation_mode_mapping: ModuleMqttMapping[CombinedValues],
        manual_controls_mapping: ModuleMqttMapping[CombinedValues],
    ):
        """Don't ever call this directly, use `MqttController#run` instead"""
        self.get_sensor_values = sensor_values_mapping.result
        self.wait_for_sensor_values = sensor_values_mapping.wait_for_result
        self.send_control_values = send_control_values
        self.send_computed_values = send_computed_values
        self.send_controller_state = send_controller_state
        self.get_parameters = parameters_mapping.result
        self.send_parameters = send_parameters
        self.send_control_modes = send_control_modes
        self.send_manual_control = send_manual_control
        self.get_automation_modes = automation_mode_mapping.result
        self.get_manual_controls = manual_controls_mapping.result

    @classmethod
    def _register(
        cls,
        connector: "MqttConnector",
        description: ControlChannelsDescription,
    ) -> "ControlChannels[S, P]":
        sensor_values_mapping = ModuleMqttMapping(
            description.sensor_values_clss,
            PartialMqttMapping,
            description.devices_topic_prefix,
        )
        connector._register_listener(sensor_values_mapping)

        parameters_mapping = ModuleMqttMapping(
            description.parameters_clss,
            DirectMqttMapping.for_module_type("parameters"),
            description.controller_topic_prefix,
            description.controller_topic_suffix,
        )
        connector._register_listener(parameters_mapping)

        manual_mode_mapping = ModuleMqttMapping(
            {key: AutomationMode for key in description.control_modes_clss.keys()},
            DirectMqttMapping.for_module_type("automation-mode"),
            description.controller_topic_prefix,
            description.controller_topic_suffix,
            allow_incomplete=True,
        )
        connector._register_listener(manual_mode_mapping)
        manual_controls_mapping = ModuleMqttMapping(
            description.control_values_clss,
            DirectMqttMapping.for_module_type("manual-values"),
            description.controller_topic_prefix,
            description.controller_topic_suffix,
        )
        connector._register_listener(manual_controls_mapping)

        return ControlChannels(
            sensor_values_mapping=sensor_values_mapping,
            send_control_values=connector._create_publisher(
                ModuleMqttMapping(
                    description.control_values_clss,
                    PartialMqttMapping,
                    description.devices_topic_prefix,
                    description.control_values_topic_suffix,
                ),
            ),
            send_computed_values=connector._create_publisher(
                ModuleMqttMapping(
                    description.sensor_values_clss,
                    PartialMqttMapping.only_computed_fields,
                    description.controller_topic_prefix,
                )
            ),
            send_controller_state=connector._create_publisher(
                ModuleMqttMapping(
                    description.controller_state_clss,
                    DirectMqttMapping.for_module_type("controller-state"),
                    description.controller_topic_prefix,
                ),
            ),
            parameters_mapping=parameters_mapping,
            send_parameters=connector._create_publisher(
                ModuleMqttMapping(
                    description.parameters_clss,
                    DirectMqttMapping.for_module_type("parameters"),
                    description.controller_topic_prefix,
                )
            ),
            send_control_modes=connector._create_publisher(
                ModuleMqttMapping(
                    description.control_modes_clss,
                    DirectMqttMapping.for_module_type("control-mode"),
                    description.controller_topic_prefix,
                )
            ),
            send_manual_control=connector._create_publisher(
                ModuleMqttMapping(
                    description.control_values_clss,
                    DirectMqttMapping.for_module_type("manual-values"),
                    description.controller_topic_prefix,
                )
            ),
            automation_mode_mapping=manual_mode_mapping,
            manual_controls_mapping=manual_controls_mapping,
        )


@dataclass
class SimulationChannelsDescription[I: SimulationInputs, O: SimulationValues]:
    devices_topic_prefix: str
    controller_topic_prefix: str
    sensor_values_clss: ModuleClassMap
    control_values_clss: ModuleClassMap
    simulation_inputs_cls: type[I]
    simulation_outputs_cls: type[O]
    control_values_topic_suffix: str
    controller_topic_suffix: str

    @staticmethod
    def from_settings[I2: SimulationInputs, O2: SimulationValues](
        config: "Config",
        control_module: "CombinedModule",
        simulation: "Simulation[ThrsValues, ThrsValues, I2, O2]",
    ) -> "SimulationChannelsDescription[I2, O2]":
        return SimulationChannelsDescription(
            devices_topic_prefix=config.mqtt_devices_topic_prefix,
            controller_topic_prefix=config.mqtt_controller_topic_prefix,
            sensor_values_clss=control_module.sensor_values_clss,
            control_values_clss=control_module.control_values_clss,
            simulation_inputs_cls=simulation.inputs_cls,
            simulation_outputs_cls=simulation.outputs_cls,
            control_values_topic_suffix=config.mqtt_control_topic_suffix,
            controller_topic_suffix=config.mqtt_controller_topic_suffix,
        )


class SimulationChannels[I: SimulationInputs, O: SimulationValues](
    Channels[SimulationChannelsDescription[I, O], "SimulationChannels[I, O]"]
):
    def __init__(
        self,
        send_sensor_values: Publisher[CombinedValues],
        control_values_mapping: ModuleMqttMapping,
        simulation_inputs_mapping: DirectMqttMapping[I],
        send_simulation_inputs: Publisher[I],
        send_simulation_outputs: Publisher[O],
    ):
        """Don't ever call this directly, use `MqttController#run` instead"""
        self.send_sensor_values = send_sensor_values
        self.get_control_values = control_values_mapping.result
        self.wait_for_control_values = control_values_mapping.wait_for_result
        self.get_simulation_inputs = simulation_inputs_mapping.result
        self.wait_for_simulation_inputs = simulation_inputs_mapping.wait_for_result
        self.send_simulation_inputs = send_simulation_inputs
        self.send_simulation_outputs = send_simulation_outputs

    @classmethod
    def _register(
        cls,
        connector: "MqttConnector",
        description: SimulationChannelsDescription[I, O],
    ) -> "SimulationChannels[I, O]":
        simulation_inputs_topic = (
            f"{description.controller_topic_prefix}/simulation-inputs"
        )
        simulation_outputs_topic = (
            f"{description.controller_topic_prefix}/simulation-outputs"
        )

        control_values_mapping = ModuleMqttMapping(
            description.control_values_clss,
            PartialMqttMapping,
            description.devices_topic_prefix,
            description.control_values_topic_suffix,
        )
        connector._register_listener(control_values_mapping)
        simulation_inputs_mapping = DirectMqttMapping(
            description.simulation_inputs_cls,
            simulation_inputs_topic,
            description.controller_topic_suffix,
        )
        connector._register_listener(simulation_inputs_mapping)
        return SimulationChannels(
            send_sensor_values=connector._create_publisher(
                ModuleMqttMapping(
                    description.sensor_values_clss,
                    PartialMqttMapping,
                    description.devices_topic_prefix,
                ),
            ),
            control_values_mapping=control_values_mapping,
            simulation_inputs_mapping=simulation_inputs_mapping,
            send_simulation_inputs=connector._create_publisher(
                DirectMqttMapping(
                    description.simulation_inputs_cls,
                    simulation_inputs_topic,
                )
            ),
            send_simulation_outputs=connector._create_publisher(
                DirectMqttMapping(
                    description.simulation_outputs_cls,
                    simulation_outputs_topic,
                ),
            ),
        )


@dataclass
class ControlApiChannelsDescription[
    S: ThrsValues,
    C: ThrsValues,
    P: ThrsValues,
    M: ThrsValues,
    CS: ThrsValues,
]:
    module_name: str
    devices_topic_prefix: str
    controller_topic_prefix: str
    sensor_values_cls: type[S]
    control_values_cls: type[C]
    controller_state_cls: type[CS]
    parameters_cls: type[P]
    control_modes_cls: type[M]
    control_values_topic_suffix: str
    controller_topic_suffix: str

    @staticmethod
    def from_settings[
        S2: ThrsValues,
        C2: ThrsValues,
        P2: ThrsValues,
        M2: ThrsValues,
        CS2: ThrsValues,
        A2: ThrsValues,
    ](
        config: "Config",
        module_name: str,
        module_description: "ModuleDescription[S2, C2, P2, M2, CS2]",
        automation_mode_cls: type[A2],
    ) -> "ControlApiChannelsDescription[S2, C2, P2, M2, CS2]":
        return ControlApiChannelsDescription(
            module_name=module_name,
            devices_topic_prefix=config.mqtt_devices_topic_prefix,
            controller_topic_prefix=config.mqtt_controller_topic_prefix,
            sensor_values_cls=module_description.sensor_values_cls,
            control_values_cls=module_description.control_values_cls,
            controller_state_cls=module_description.controller_state_cls,
            parameters_cls=module_description.parameters_cls,
            control_modes_cls=module_description.control_mode_cls,
            control_values_topic_suffix=config.mqtt_control_topic_suffix,
            controller_topic_suffix=config.mqtt_controller_topic_suffix,
        )


class ControlApiChannels[
    S: ThrsValues,
    C: ThrsValues,
    P: ThrsValues,
    M: ThrsValues,
    CS: ThrsValues,
](
    Channels[
        ControlApiChannelsDescription[S, C, P, M, CS],
        "ControlApiChannels[S, C, P, M, CS]",
    ]
):
    def __init__(
        self,
        sensor_values_mapping: PartialMqttMapping[S],
        control_values_mapping: PartialMqttMapping[C],
        manual_values_mapping: DirectMqttMapping[C],
        control_modes_mapping: DirectMqttMapping[M],
        parameters_mapping: DirectMqttMapping[P],
        controller_state_mapping: DirectMqttMapping[CS],
        send_manual_values: Publisher[C],
        send_automation_mode: Publisher[AutomationMode],
        send_parameters: Publisher[P],
    ):
        """Don't ever call this directly, use `MqttConnector#run` instead"""
        self.get_sensor_values = sensor_values_mapping.result
        self.get_control_values = control_values_mapping.result
        self.get_manual_values = manual_values_mapping.result
        self.get_control_modes = control_modes_mapping.result
        self.get_parameters = parameters_mapping.result
        self.get_controller_state = controller_state_mapping.result
        self.wait_for_manual_values = manual_values_mapping.wait_for
        self.wait_for_parameters = parameters_mapping.wait_for
        self.wait_for_control_modes = control_modes_mapping.wait_for
        self.send_manual_values = send_manual_values
        self.send_automation_mode = send_automation_mode
        self.send_parameters = send_parameters

    @classmethod
    def _register(
        cls,
        connector: "MqttConnector",
        description: ControlApiChannelsDescription[S, C, P, M, CS],
    ) -> "ControlApiChannels[S, C, P, M, CS]":
        sensor_values_mapping = PartialMqttMapping(
            description.sensor_values_cls,
            description.devices_topic_prefix,
            description.module_name,
        )
        connector._register_listener(sensor_values_mapping)

        control_values_mapping = PartialMqttMapping(
            description.control_values_cls,
            description.devices_topic_prefix,
            description.module_name,
            description.control_values_topic_suffix,
        )
        connector._register_listener(control_values_mapping)

        manual_values_mapping = DirectMqttMapping.for_module(
            description.control_values_cls,
            description.controller_topic_prefix,
            description.module_name,
            type_topic="manual-values",
        )
        connector._register_listener(manual_values_mapping)

        control_modes_mapping = DirectMqttMapping.for_module(
            SwitchingControlMode[description.control_modes_cls],
            description.controller_topic_prefix,
            description.module_name,
            type_topic="control-mode",
        )
        connector._register_listener(control_modes_mapping)

        parameters_mapping = DirectMqttMapping.for_module(
            description.parameters_cls,
            description.controller_topic_prefix,
            description.module_name,
            type_topic="parameters",
        )
        connector._register_listener(parameters_mapping)

        controller_state_mapping = DirectMqttMapping.for_module(
            description.controller_state_cls,
            description.controller_topic_prefix,
            description.module_name,
            type_topic="controller-state",
        )
        connector._register_listener(controller_state_mapping)

        return ControlApiChannels(
            sensor_values_mapping=sensor_values_mapping,
            control_values_mapping=control_values_mapping,
            manual_values_mapping=manual_values_mapping,
            control_modes_mapping=control_modes_mapping,
            parameters_mapping=parameters_mapping,
            controller_state_mapping=controller_state_mapping,
            send_manual_values=connector._create_publisher(
                DirectMqttMapping.for_module(
                    description.control_values_cls,
                    description.controller_topic_prefix,
                    description.module_name,
                    description.controller_topic_suffix,
                    type_topic="manual-values",
                ),
            ),
            send_automation_mode=connector._create_publisher(
                DirectMqttMapping.for_module(
                    AutomationMode,
                    description.controller_topic_prefix,
                    description.module_name,
                    description.controller_topic_suffix,
                    type_topic="automation-mode",
                ),
            ),
            send_parameters=connector._create_publisher(
                DirectMqttMapping.for_module(
                    description.parameters_cls,
                    description.controller_topic_prefix,
                    description.module_name,
                    description.controller_topic_suffix,
                    type_topic="parameters",
                ),
            ),
        )


@dataclass
class SimulationApiChannelsDescription[I: SimulationInputs, O: SimulationValues]:
    controller_topic_prefix: str
    controller_topic_suffix: str
    simulation_inputs_cls: type[I] | tuple[type[I], ...]
    simulation_outputs_cls: type[O] | tuple[type[O], ...]

    @staticmethod
    def from_settings[I2: SimulationInputs, O2: SimulationValues](
        config: "Config",
        simulation_inputs_cls: type[I2] | tuple[type[I2], ...],
        simulation_outputs_cls: type[O2] | tuple[type[O2], ...],
    ) -> "SimulationApiChannelsDescription[I2, O2]":
        return SimulationApiChannelsDescription(
            controller_topic_prefix=config.mqtt_controller_topic_prefix,
            controller_topic_suffix=config.mqtt_controller_topic_suffix,
            simulation_inputs_cls=simulation_inputs_cls,
            simulation_outputs_cls=simulation_outputs_cls,
        )


class SimulationApiChannels[I: SimulationInputs, O: SimulationValues](
    Channels[SimulationApiChannelsDescription[I, O], "SimulationApiChannels[I, O]"]
):
    def __init__(
        self,
        simulation_inputs_mapping: DirectMqttMapping[I],
        simulation_outputs_mapping: DirectMqttMapping[O],
        send_simulation_inputs: Publisher[I],
    ):
        """Don't ever call this directly, use `MqttConnector#run` instead"""
        self.get_simulation_inputs = simulation_inputs_mapping.result
        self.wait_for_simulation_inputs = simulation_inputs_mapping.wait_for_result
        self.get_simulation_outputs = simulation_outputs_mapping.result
        self.wait_for_simulation_outputs = simulation_outputs_mapping.wait_for_result
        self.wait_for_simulation_inputs_where = simulation_inputs_mapping.wait_for
        self.wait_for_simulation_outputs_where = simulation_outputs_mapping.wait_for
        self.send_simulation_inputs = send_simulation_inputs

    @classmethod
    def _register(
        cls,
        connector: "MqttConnector",
        description: SimulationApiChannelsDescription[I, O],
    ) -> "SimulationApiChannels[I, O]":
        simulation_inputs_mapping = DirectMqttMapping(
            description.simulation_inputs_cls,
            f"{description.controller_topic_prefix}/simulation-inputs",
        )
        connector._register_listener(simulation_inputs_mapping)

        simulation_outputs_mapping = DirectMqttMapping(
            description.simulation_outputs_cls,
            f"{description.controller_topic_prefix}/simulation-outputs",
        )
        connector._register_listener(simulation_outputs_mapping)

        return SimulationApiChannels(
            simulation_inputs_mapping=simulation_inputs_mapping,
            simulation_outputs_mapping=simulation_outputs_mapping,
            send_simulation_inputs=connector._create_publisher(
                DirectMqttMapping(
                    description.simulation_inputs_cls,
                    f"{description.controller_topic_prefix}/simulation-inputs/{description.controller_topic_suffix}",
                ),
            ),
        )


@dataclass
class DirectivesChannelsDescription:
    controller_topic_prefix: str

    @staticmethod
    def from_settings(config: "Config") -> "DirectivesChannelsDescription":
        return DirectivesChannelsDescription(
            controller_topic_prefix=config.mqtt_controller_topic_prefix,
        )


class DirectivesChannels(Channels[DirectivesChannelsDescription, "DirectivesChannels"]):
    def __init__(
        self,
        play_mapping: DirectMqttMapping[PlayMessage],
        step_mapping: DirectMqttMapping[StepMessage],
        pause_mapping: DirectMqttMapping[PauseMessage],
        send_simulation_status: Publisher[SimulationStatusMessage],
        clear_simulation_status: Callable[[], Awaitable[None]],
    ):
        self.on_play = play_mapping.add_hook
        self.on_step = step_mapping.add_hook
        self.on_pause = pause_mapping.add_hook
        self.send_simulation_status = send_simulation_status
        self.clear_simulation_status = clear_simulation_status

    @classmethod
    def _register(
        cls,
        connector: "MqttConnector",
        description: DirectivesChannelsDescription,
    ) -> "DirectivesChannels":
        play_mapping = DirectMqttMapping(
            PlayMessage,
            f"{description.controller_topic_prefix}/{PlayMessage.subscribe_topic()}",
        )
        connector._register_listener(play_mapping)

        step_mapping = DirectMqttMapping(
            StepMessage,
            f"{description.controller_topic_prefix}/{StepMessage.subscribe_topic()}",
        )
        connector._register_listener(step_mapping)

        pause_mapping = DirectMqttMapping(
            PauseMessage,
            f"{description.controller_topic_prefix}/{PauseMessage.subscribe_topic()}",
        )
        connector._register_listener(pause_mapping)

        status_topic = f"{description.controller_topic_prefix}/{SimulationStatusMessage.subscribe_topic()}"

        async def _clear_simulation_status():
            await connector._mqtt_client.publish(status_topic, b"", qos=1, retain=True)

        return DirectivesChannels(
            play_mapping=play_mapping,
            step_mapping=step_mapping,
            pause_mapping=pause_mapping,
            send_simulation_status=connector._create_publisher(
                DirectMqttMapping(SimulationStatusMessage, status_topic), retain=True
            ),
            clear_simulation_status=_clear_simulation_status,
        )


@dataclass
class DirectivesApiChannelsDescription:
    controller_topic_prefix: str

    @staticmethod
    def from_settings(config: "Config") -> "DirectivesApiChannelsDescription":
        return DirectivesApiChannelsDescription(
            controller_topic_prefix=config.mqtt_controller_topic_prefix,
        )


class DirectivesApiChannels(
    Channels[DirectivesApiChannelsDescription, "DirectivesApiChannels"]
):
    def __init__(
        self,
        simulation_status_mapping: DirectMqttMapping[SimulationStatusMessage],
        _send_play: Publisher[PlayMessage],
        _send_step: Publisher[StepMessage],
        _send_pause: Publisher[PauseMessage],
    ):
        self.get_simulation_status = simulation_status_mapping.result
        self.wait_for_simulation_status = simulation_status_mapping.wait_for_result
        self.wait_for_simulation_status_where = simulation_status_mapping.wait_for
        self.on_simulation_status = simulation_status_mapping.add_hook
        self._send_play = _send_play
        self._send_step = _send_step
        self._send_pause = _send_pause

    async def send_play(self, playback_rate: float):
        await self._send_play(PlayMessage(playback_rate=playback_rate))

    async def send_step(self, seconds: float):
        await self._send_step(StepMessage(seconds=seconds))

    async def send_pause(self):
        await self._send_pause(PauseMessage())

    @classmethod
    def _register(
        cls,
        connector: "MqttConnector",
        description: DirectivesApiChannelsDescription,
    ) -> "DirectivesApiChannels":
        status_topic = f"{description.controller_topic_prefix}/{SimulationStatusMessage.subscribe_topic()}"
        simulation_status_mapping = DirectMqttMapping(
            SimulationStatusMessage, status_topic
        )
        connector._register_listener(simulation_status_mapping)

        return DirectivesApiChannels(
            simulation_status_mapping=simulation_status_mapping,
            _send_play=connector._create_publisher(
                DirectMqttMapping(
                    PlayMessage,
                    f"{description.controller_topic_prefix}/{PlayMessage.subscribe_topic()}",
                )
            ),
            _send_step=connector._create_publisher(
                DirectMqttMapping(
                    StepMessage,
                    f"{description.controller_topic_prefix}/{StepMessage.subscribe_topic()}",
                )
            ),
            _send_pause=connector._create_publisher(
                DirectMqttMapping(
                    PauseMessage,
                    f"{description.controller_topic_prefix}/{PauseMessage.subscribe_topic()}",
                )
            ),
        )


class MqttConnector:
    def __init__(self, mqtt_client: Client):
        self._mqtt_client = mqtt_client
        self._listeners: list[MqttReceiveMapping[object]] = []

    @property
    def listeners(self) -> list[MqttReceiveMapping[object]]:
        return self._listeners

    def clear_listeners(self):
        self._listeners.clear()

    def build(self) -> MqttConnectorBuilder[()]:
        return MqttConnectorBuilder(self)

    def _register_listener[T](
        self, receiver: MqttReceiveMapping[T]
    ) -> MqttReceiveMapping[T]:
        self._listeners.append(receiver)
        return receiver

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
                    mapping.handle_message(message.topic.value, message.payload)

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

    async def run[D, C](
        self, channels_type: type[Channels[D, C]], description: D
    ) -> tuple[C, Coroutine[None, None, None]]:
        channels = channels_type._register(self, description)
        await self._start()
        return channels, self._listen()
