from asyncio import Queue
import asyncio
from typing import Callable, Coroutine, Literal
from aiomqtt import Client as MqttClient, Message, Topic
from dataclasses import dataclass

from thrs.cli.simulation_controls import (
    ControlModeMessage,
    ManualControlMessage,
    ParametersMessage,
    PauseMessage,
    PlayMessage,
    SetParametersMessage,
    SetSimulationInputsMessage,
    SimulationInputMessage,
    SimulationStatusMessage,
    StepMessage,
    SetAutomationMessage,
)
from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsValues
from thrs.input_output.model_builder import PartialModelBuilder
from thrs.utils.string import dash_to_snake
from thrs.orchestration.config import Config


@dataclass
class Context:
    modules: "list[MessagingModule]"


class MessageReceiver[T: ThrsValues]:
    def __init__(self, cls: type[T], topic: str):
        self._cls = cls
        self._last: T | None = None
        self._waiting = False
        self._msgs = Queue[T]()
        self._topic = f"{settings.mqtt_topic_prefix}/{topic}"

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
        return topic.matches(self.subscribe_topic)

    @property
    def subscribe_topic(self):
        return self._topic


class PartialMessageReceiver[T: ThrsValues](MessageReceiver[T]):
    def __init__(
        self, cls: type[T], topic_prefix: str, topic_suffix: str | None = None
    ):
        super().__init__(cls, topic_prefix)
        self._model_builder = PartialModelBuilder(cls)
        self._topic_prefix = topic_prefix
        self._topic_suffix = topic_suffix

    def _parse_message(self, message: Message) -> T | None:
        if not isinstance(message.payload, str | bytes):
            raise ValueError(f"Expected string or bytes, got {type(message.payload)}")
        key = message.topic.value.removeprefix(f"{self._topic_prefix}/")
        if self._topic_suffix:
            key = key.removesuffix(f"/{self._topic_suffix}")
        self._model_builder.input(dash_to_snake(key), message.payload)
        return self._model_builder.result()

    @property
    def subscribe_topic(self):
        return (
            f"{self._topic_prefix}/+/{self._topic_suffix}"
            if self._topic_suffix
            else f"{self._topic_prefix}/+"
        )


class SimulationStatusMessageReceiver(MessageReceiver[SimulationStatusMessage]):
    async def handle(self, msg: Message, context: Context):
        parsed = self._parse_message(msg)
        if parsed is not None:
            for module in context.modules:
                module.active = module.name in parsed.modules

        await super().handle(msg, context)


settings = Config()  # type: ignore


class MessagingModule[
    SensorValues: ThrsValues,
    ControlValues: ThrsValues,
    Parameters: ThrsValues,
    Inputs: SimulationInputs,
    Outputs: SimulationValues,
    Mode,
]:
    def __init__(
        self,
        name: str,
        sensor_values_cls: type[SensorValues],
        control_values_cls: type[ControlValues],
        parameters_cls: type[Parameters],
        simulation_inputs_cls: type[Inputs],
        simulation_outputs_cls: type[Outputs],
        mode_cls: type[Mode],
        mqtt_client: MqttClient,
    ):
        self.name = name
        self._active = False
        self.sensor_values_cls = sensor_values_cls
        self.control_values_cls = control_values_cls

        topic_prefix = f"{settings.mqtt_topic_prefix}/{name}"
        self._sensor_values = PartialMessageReceiver(sensor_values_cls, topic_prefix)
        self._control_values = PartialMessageReceiver(
            control_values_cls, topic_prefix, settings.mqtt_control_topic_suffix
        )

        self._parameters = MessageReceiver(
            ParametersMessage[parameters_cls], ParametersMessage.subscribe_topic()
        )
        self._simulation_inputs = MessageReceiver(
            SimulationInputMessage[simulation_inputs_cls],
            SimulationInputMessage.subscribe_topic(),
        )
        self._simulation_outputs = MessageReceiver(
            simulation_outputs_cls,
            "simulation/outputs",
        )
        self._control_mode = MessageReceiver(
            ControlModeMessage[mode_cls], ControlModeMessage.subscribe_topic()
        )
        self._mqtt_client = mqtt_client

    @property
    def receivers(self):
        return [
            self._sensor_values,
            self._control_values,
            self._parameters,
            self._simulation_inputs,
            self._simulation_outputs,
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
        message = ManualControlMessage(module=self.name, control_values=control_values)
        await self._mqtt_client.publish(
            f"{settings.mqtt_topic_prefix}/{message.topic()}",
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

    def wait_for_simulation_inputs(
        self,
        condition: Callable[[Inputs], bool],
        *_args,
        timeout: float,
    ) -> Coroutine[None, None, Inputs]:
        async def _afterwards(wait):
            return (await wait).inputs

        return _afterwards(
            self._simulation_inputs.wait_for(lambda msg: condition(msg.inputs), timeout)
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

    @property
    def simulation_inputs(self) -> Inputs | None:
        return (
            self._simulation_inputs.last.inputs
            if self._simulation_inputs.last
            else None
        )

    @property
    def simulation_outputs(self) -> Outputs | None:
        return self._simulation_outputs.last

    async def set_parameters(self, parameters: Parameters):
        message = SetParametersMessage[Parameters](
            module=self.name, parameters=parameters
        )
        await self._mqtt_client.publish(
            f"{settings.mqtt_topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
        )

    async def set_simulation_inputs(self, inputs: Inputs):
        message = SetSimulationInputsMessage[Inputs](inputs=inputs)
        await self._mqtt_client.publish(
            f"{settings.mqtt_topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
        )

    async def set_automation_mode(self, enabled: bool):
        message = SetAutomationMessage(module=self.name, enabled=enabled)
        await self._mqtt_client.publish(
            f"{settings.mqtt_topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
        )

    def wait_for_control_mode(
        self, automatic: bool, *_args, timeout: float
    ) -> Coroutine[None, None, ControlModeMessage]:
        return self._control_mode.wait_for(lambda m: m.mode == automatic, timeout)

    @property
    def control_mode(self) -> ControlModeMessage | None:
        return self._control_mode.last


class Messaging:
    def __init__(
        self,
        mqtt_client: MqttClient,
        modules: list[MessagingModule],
    ):
        self._mqtt_client = mqtt_client
        self._modules = modules
        self._simulation_status = SimulationStatusMessageReceiver(
            SimulationStatusMessage, SimulationStatusMessage.subscribe_topic()
        )

    @property
    def _all_receivers(self):
        return [
            self._simulation_status,
            *[receiver for module in self._modules for receiver in module.receivers],
        ]

    @property
    def _active_receivers(self):
        return [
            self._simulation_status,
            *[
                receiver
                for module in self._modules
                if module.active
                for receiver in module.receivers
            ],
        ]

    async def run(self) -> Coroutine[None, None, None]:
        topics = set(receiver.subscribe_topic for receiver in self._all_receivers)
        await self._mqtt_client.subscribe(SimulationStatusMessage.subscribe_topic())
        await asyncio.sleep(0.2)  # Give status time to arrive first
        for topic in topics:
            if topic != SimulationStatusMessage.subscribe_topic():
                await self._mqtt_client.subscribe(topic, qos=1)

        async def _run(self):
            context = Context(modules=self._modules)
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
            f"{settings.mqtt_topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
        )

    async def pause_simulation(self):
        message = PauseMessage()
        await self._mqtt_client.publish(
            f"{settings.mqtt_topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
        )

    async def step_simulation(self, seconds: float):
        message = StepMessage(seconds=seconds)
        await self._mqtt_client.publish(
            f"{settings.mqtt_topic_prefix}/{message.topic()}",
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
