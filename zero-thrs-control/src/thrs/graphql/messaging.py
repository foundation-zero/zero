import asyncio
from asyncio import Queue
from dataclasses import dataclass
from time import monotonic
from typing import Callable, Coroutine, Literal

from aiomqtt import Client as MqttClient
from aiomqtt import Message, Topic

from thrs.cli.simulation_controls import (
    ControlModeMessage,
    ManualControlMessage,
    ParametersMessage,
    PauseMessage,
    PlayMessage,
    SetAutomationMessage,
    SetParametersMessage,
    SetSimulationInputsMessage,
    SimulationInputMessage,
    SimulationStatusMessage,
    StepMessage,
)
from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsValues
from thrs.orchestration.connector import PartialMqttMapping
from thrs.orchestration.module import ModuleDescription


@dataclass
class Context:
    control_modules: "list[ControlMessaging]"
    simulation: "SimulationMessaging"


class MessageReceiver[T: ThrsValues]:
    def __init__(self, cls: type[T], topic: str):
        self._cls = cls
        self._last: T | None = None
        self._waiting = False
        self._msgs = Queue[T]()
        self._topic = topic

    @property
    def last(self) -> T | None:
        return self._last

    def wait_for(
        self, condition: Callable[[T], bool], timeout: float
    ) -> Coroutine[None, None, T]:
        # Waiting is done a bit awkward to ensure self._waiting is True directly after the call
        # Otherwise we might miss message if those arrive right after calling this function
        # and before asyncio ran `self._waiting = True`
        self._waiting = True

        async def _wait():
            async with asyncio.timeout(timeout):
                try:
                    while True:
                        msg = await self._msgs.get()
                        if condition(msg):
                            return msg
                finally:
                    self._waiting = False

        return _wait()

    async def handle(self, msg: Message, context: Context):
        parsed = self._parse_message(msg)
        self._last = parsed
        if self._waiting and parsed is not None:
            await self._msgs.put(parsed)

    def _parse_message(self, message: Message) -> T | None:
        if not isinstance(message.payload, str | bytes):
            raise ValueError(f"Expected string or bytes, got {type(message.payload)}")
        return self._cls.model_validate_json(message.payload)

    @property
    def cls(self):
        return self._cls

    def matches(self, topic: Topic) -> bool:
        return any(
            topic.matches(subscribe_topic) for subscribe_topic in self.subscribe_topics
        )

    @property
    def subscribe_topics(self):
        return {self._topic}


class PartialMessageReceiver[T: ThrsValues](MessageReceiver[T]):
    def __init__(
        self,
        cls: type[T],
        topic_prefix: str,
        module_name: str,
        topic_suffix: str | None = None,
    ):
        super().__init__(cls, topic_prefix)
        self._mqtt_mapping = PartialMqttMapping(
            cls, topic_prefix, module_name, topic_suffix
        )
        self._topic_suffix = topic_suffix

    def _parse_message(self, message: Message) -> T | None:
        if not isinstance(message.payload, str | bytes):
            raise ValueError(f"Expected string or bytes, got {type(message.payload)}")
        topic = message.topic.value
        if self._topic_suffix:
            topic = topic.removesuffix(f"/{self._topic_suffix}")
        self._mqtt_mapping.handle_message(message.topic.value, message.payload)
        return self._mqtt_mapping.result()

    @property
    def subscribe_topics(self):
        return self._mqtt_mapping.subscribe_topics()


class SimulationStatusMessageReceiver(MessageReceiver[SimulationStatusMessage]):
    async def handle(self, msg: Message, context: Context):
        parsed = self._parse_message(msg)
        if parsed is not None:
            for module in context.control_modules:
                module.active = module.module_name in parsed.control_modules
            await context.simulation.select_mode(parsed.mode)

        await super().handle(msg, context)


class ControlMessaging[
    SensorValues: ThrsValues,
    ControlValues: ThrsValues,
    Parameters: ThrsValues,
    Mode: ThrsValues,
]:
    def __init__(
        self,
        module_name: str,
        module_description: ModuleDescription[
            SensorValues, ControlValues, Parameters, Mode
        ],
        mqtt_client: MqttClient,
        devices_topic_prefix: str,
        controller_topic_prefix: str,
        control_topic_suffix: str | None = None,
    ):
        self.module_name = module_name
        self._active = False
        self.sensor_values_cls = module_description.sensor_values_cls
        self.control_values_cls = module_description.control_values_cls

        self._devices_topic_prefix = devices_topic_prefix
        self._controller_topic_prefix = controller_topic_prefix
        self._sensor_values = PartialMessageReceiver(
            module_description.sensor_values_cls,
            self._devices_topic_prefix,
            module_name,
        )
        self._control_values = PartialMessageReceiver(
            module_description.control_values_cls,
            self._devices_topic_prefix,
            module_name,
            control_topic_suffix,
        )

        self._parameters = MessageReceiver(
            ParametersMessage[module_description.parameters_cls],
            f"{self._controller_topic_prefix}/{ParametersMessage.subscribe_topic()}",
        )
        self._control_mode = MessageReceiver(
            ControlModeMessage[module_description.control_mode_cls],
            f"{self._controller_topic_prefix}/{ControlModeMessage.subscribe_topic()}",
        )
        self._mqtt_client = mqtt_client

    @property
    def receivers(self):
        return [
            self._sensor_values,
            self._control_values,
            self._parameters,
            self._control_mode,
        ]

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool):
        self._active = value

    async def send_manual_controls(self, control_values: ControlValues):
        if not self._active:
            raise Exception("Cannot send manual controls to inactive module")
        message = ManualControlMessage(
            module=self.module_name, control_values=control_values
        )
        await self._mqtt_client.publish(
            f"{self._controller_topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
        )

    def wait_for_control_values(
        self, condition: Callable[[ControlValues], bool], *_args, timeout: float
    ) -> Coroutine[None, None, ControlValues]:
        return self._control_values.wait_for(condition, timeout)

    def wait_for_parameters(
        self, condition: Callable[[Parameters], bool], *_args, timeout: float
    ) -> Coroutine[None, None, Parameters]:
        async def _afterwards(wait):
            return (await wait).parameters

        return _afterwards(
            self._parameters.wait_for(lambda msg: condition(msg.parameters), timeout)
        )

    @property
    def sensor_values(self) -> SensorValues | None:
        return self._sensor_values.last

    @property
    def control_values(self) -> ControlValues | None:
        return self._control_values.last

    @property
    def parameters(self) -> Parameters | None:
        return self._parameters.last.parameters if self._parameters.last else None

    async def set_parameters(self, parameters: Parameters):
        message = SetParametersMessage[Parameters](
            module=self.module_name, parameters=parameters
        )
        await self._mqtt_client.publish(
            f"{self._controller_topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
        )

    async def set_automation_mode(self, enabled: bool):
        message = SetAutomationMessage(module=self.module_name, enabled=enabled)
        await self._mqtt_client.publish(
            f"{self._controller_topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
        )

    def wait_for_control_mode(
        self, automatic: bool, *_args, timeout: float
    ) -> Coroutine[None, None, ControlModeMessage]:
        return self._control_mode.wait_for(
            lambda m: m.mode.automatic == automatic, timeout
        )

    @property
    def control_mode(self) -> ControlModeMessage | None:
        return self._control_mode.last


class RawMessageReceiver[T: ThrsValues](MessageReceiver[T]):
    def __init__(self, cls: type[T], topic: str):
        super().__init__(cls, topic)
        self._timestamp = None
        self._message = None
        self._context = None

    async def handle(self, msg: Message, context: Context):
        self._message = msg
        self._context = context
        self._timestamp = monotonic()

    @property
    def message(self) -> Message | None:
        return self._message

    @property
    def context(self) -> Context | None:
        return self._context

    def seconds_passed_since_last_message(self) -> float | None:
        if self._timestamp is None:
            return None
        return monotonic() - self._timestamp


REPROCESS_SIMULATION_VALUES_TIMEOUT = 5  # seconds


class SimulationMessaging:
    def __init__(
        self,
        mapping: dict[str, tuple[type[SimulationInputs], type[SimulationValues]]],
        mqtt_client: MqttClient,
        simulation_topic_prefix: str,
    ):
        self._mode = None
        self._mapping = mapping
        self._mqtt_client = mqtt_client
        self._simulation_inputs = RawMessageReceiver(
            SimulationInputMessage[SimulationInputs],
            f"{simulation_topic_prefix}/{SimulationInputMessage.subscribe_topic()}",
        )
        self._simulation_outputs = RawMessageReceiver(
            SimulationValues, f"{simulation_topic_prefix}/outputs"
        )
        self._simulation_inputs_cls = None
        self._simulation_topic_prefix = simulation_topic_prefix

    @property
    def receivers(self):
        return [
            self._simulation_inputs,
            self._simulation_outputs,
        ]

    async def select_mode(self, mode: str):
        if mode == self._mode:
            return
        self._mode = mode
        simulation_inputs_cls, simulation_outputs_cls = self._mapping[mode]

        inputs = MessageReceiver(
            SimulationInputMessage[simulation_inputs_cls],
            f"{self._simulation_topic_prefix}/{SimulationInputMessage.subscribe_topic()}",
        )
        outputs = MessageReceiver(
            simulation_outputs_cls,
            f"{self._simulation_topic_prefix}/outputs",
        )
        await self._try_reprocess(inputs, self._simulation_inputs)
        await self._try_reprocess(outputs, self._simulation_outputs)
        self._simulation_inputs = inputs
        self._simulation_outputs = outputs
        self._simulation_inputs_cls = simulation_inputs_cls

    async def _try_reprocess(self, new, old):
        if isinstance(old, RawMessageReceiver) and (
            (passed := old.seconds_passed_since_last_message())
            and (passed < REPROCESS_SIMULATION_VALUES_TIMEOUT)
            and old.message is not None
            and old.context is not None
        ):
            await new.handle(
                old.message,
                old.context,
            )

    def wait_for_simulation_inputs(
        self,
        condition: Callable[[SimulationInputs], bool],
        *_args,
        timeout: float,
    ) -> Coroutine[None, None, SimulationInputs]:
        async def _afterwards(wait):
            return (await wait).inputs

        return _afterwards(
            self._simulation_inputs.wait_for(lambda msg: condition(msg.inputs), timeout)
            if self._simulation_inputs
            else None
        )

    @property
    def mode(self) -> str | None:
        return self._mode

    @property
    def simulation_inputs(self) -> SimulationInputs | None:
        return (
            self._simulation_inputs.last.inputs
            if self._simulation_inputs and self._simulation_inputs.last
            else None
        )

    @property
    def simulation_outputs(self) -> SimulationValues | None:
        return self._simulation_outputs.last if self._simulation_outputs else None

    async def set_simulation_inputs(self, inputs: SimulationInputs):
        if self._simulation_inputs_cls is None:
            raise Exception(
                "Cannot set simulation inputs before simulation mode is selected"
            )
        message = SetSimulationInputsMessage[self._simulation_inputs_cls](inputs=inputs)
        await self._mqtt_client.publish(
            f"{self._simulation_topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
        )


class Messaging:
    def __init__(
        self,
        mqtt_client: MqttClient,
        control_modules: list[ControlMessaging],
        simulation: SimulationMessaging,
        simulation_topic_prefix: str,
    ):
        self._mqtt_client = mqtt_client
        self._control_modules = control_modules
        self._simulation = simulation
        self._simulation_status = SimulationStatusMessageReceiver(
            SimulationStatusMessage,
            f"{simulation_topic_prefix}/{SimulationStatusMessage.subscribe_topic()}",
        )
        self._simulation_topic_prefix = simulation_topic_prefix

    @property
    def _all_receivers(self):
        return [
            self._simulation_status,
            *self._simulation.receivers,
            *[
                receiver
                for module in self._control_modules
                for receiver in module.receivers
            ],
        ]

    @property
    def _active_receivers(self):
        return [
            self._simulation_status,
            *self._simulation.receivers,
            *[
                receiver
                for module in self._control_modules
                if module.active
                for receiver in module.receivers
            ],
        ]

    async def run(self) -> Coroutine[None, None, None]:
        topics = set(
            topic
            for receiver in self._all_receivers
            for topic in receiver.subscribe_topics
        )
        await self._mqtt_client.subscribe(SimulationStatusMessage.subscribe_topic())
        await asyncio.sleep(0.2)  # Give status time to arrive first
        for topic in topics - {SimulationStatusMessage.subscribe_topic()}:
            await self._mqtt_client.subscribe(topic, qos=1)

        async def _run(self):
            context = Context(
                control_modules=self._control_modules, simulation=self._simulation
            )
            async for message in self._mqtt_client.messages:
                if message.payload == b"":
                    continue

                if receiver := self.match_receiver(message):
                    await receiver.handle(message, context)

        return _run(self)

    def match_receiver(self, message: Message) -> MessageReceiver | None:
        for receiver in self._active_receivers:
            if receiver.matches(message.topic):
                return receiver
        return None

    async def play_simulation(self, playback_rate: float):
        message = PlayMessage(playback_rate=playback_rate)
        await self._mqtt_client.publish(
            f"{self._simulation_topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
        )

    async def pause_simulation(self):
        message = PauseMessage()
        await self._mqtt_client.publish(
            f"{self._simulation_topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
        )

    async def step_simulation(self, seconds: float):
        message = StepMessage(seconds=seconds)
        await self._mqtt_client.publish(
            f"{self._simulation_topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
        )

    def wait_for_simulation_status(
        self,
        status: Literal["stepping", "running", "available"],
        *_args,
        timeout: float,
    ) -> Coroutine[None, None, SimulationStatusMessage]:
        return self._simulation_status.wait_for(lambda s: s.status == status, timeout)

    @property
    def simulation_status(self) -> SimulationStatusMessage | None:
        return self._simulation_status.last
