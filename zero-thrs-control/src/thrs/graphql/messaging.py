from asyncio import Queue
import asyncio
from typing import Callable, Coroutine, Literal
from aiomqtt import Client as MqttClient, Message
from dataclasses import dataclass

from thrs.cli.simulation_controls import (
    ControlStatusMessage,
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
from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsModel


@dataclass
class Context:
    modules: "list[MessagingModule]"


class MessageReceiver[T: ThrsModel]:
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

    async def handle(self, msg: T, context: Context):
        self._last = msg
        if self._waiting:
            await self._msgs.put(msg)

    @property
    def cls(self):
        return self._cls

    @property
    def topic(self):
        return self._topic


class SimulationStatusMessageReceiver(MessageReceiver[SimulationStatusMessage]):
    async def handle(self, msg: SimulationStatusMessage, context: Context):
        for module in context.modules:
            module.active = module.name == msg.module

        await super().handle(msg, context)


class MessagingModule[
    SensorValues: ThrsModel,
    ControlValues: ThrsModel,
    Parameters: ThrsModel,
    Inputs: SimulationInputs,
    Outputs: SimulationValues,
]:
    def __init__(
        self,
        name: str,
        sensor_values_cls: type[SensorValues],
        control_values_cls: type[ControlValues],
        parameters_cls: type[Parameters],
        simulation_inputs_cls: type[Inputs],
        simulation_outputs_cls: type[Outputs],
        mqtt_client: MqttClient,
    ):
        self.name = name
        self._active = False
        self.sensor_values_cls = sensor_values_cls
        self.control_values_cls = control_values_cls
        self._sensor_values = MessageReceiver(sensor_values_cls, "thrs/sensor_values")
        self._control_values = MessageReceiver(
            control_values_cls, "thrs/control_values"
        )
        self._parameters = MessageReceiver(
            ParametersMessage[parameters_cls], ParametersMessage.topic()
        )
        self._simulation_inputs = MessageReceiver(
            SimulationInputMessage[simulation_inputs_cls],
            SimulationInputMessage.topic(),
        )
        self._simulation_outputs = MessageReceiver(
            simulation_outputs_cls,
            "thrs/simulation/outputs",
        )
        self._mqtt_client = mqtt_client

    @property
    def receivers(self):
        return [
            self._sensor_values,
            self._control_values,
            self._parameters,
            self._simulation_inputs,
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
        await self._mqtt_client.publish(
            ManualControlMessage.topic(),
            ManualControlMessage(control_values=control_values).model_dump_json(),
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
        await self._mqtt_client.publish(
            SetParametersMessage[Parameters].topic(),
            SetParametersMessage[Parameters](parameters=parameters).model_dump_json(),
            qos=1,
        )

    async def set_simulation_inputs(self, inputs: Inputs):
        await self._mqtt_client.publish(
            SetSimulationInputsMessage[Inputs].topic(),
            SetSimulationInputsMessage[Inputs](inputs=inputs).model_dump_json(),
            qos=1,
        )


class Messaging:
    def __init__(
        self,
        mqtt_client: MqttClient,
        modules: list[MessagingModule],
    ):
        self._mqtt_client = mqtt_client
        self._modules = modules
        self._simulation_status = SimulationStatusMessageReceiver(
            SimulationStatusMessage, SimulationStatusMessage.topic()
        )
        self._control_status = MessageReceiver(
            ControlStatusMessage, ControlStatusMessage.topic()
        )

    @property
    def _all_receivers(self):
        return [
            self._simulation_status,
            self._control_status,
            *[receiver for module in self._modules for receiver in module.receivers],
        ]

    @property
    def _active_receivers(self):
        return [
            self._simulation_status,
            self._control_status,
            *[
                receiver
                for module in self._modules
                if module.active
                for receiver in module.receivers
            ],
        ]

    async def run(self) -> Coroutine[None, None, None]:
        topics = set(receiver.topic for receiver in self._all_receivers)
        await self._mqtt_client.subscribe(SimulationStatusMessage.topic())
        await asyncio.sleep(0.2)  # Give status time to arrive first
        for topic in topics:
            if topic != SimulationStatusMessage.topic():
                await self._mqtt_client.subscribe(topic, qos=1)

        async def _run(self):
            context = Context(modules=self._modules)
            async for message in self._mqtt_client.messages:
                if message.payload == b"":
                    continue

                if receiver := self.match_receiver(message):
                    await receiver.handle(
                        self._parse_message(message, receiver.cls), context
                    )

        return _run(self)

    def match_receiver(self, message: Message) -> MessageReceiver | None:
        for status in self._active_receivers:
            if message.topic.matches(status.topic):
                return status
        return None

    async def play_simulation(self, playback_rate: float):
        await self._mqtt_client.publish(
            PlayMessage.topic(),
            PlayMessage(playback_rate=playback_rate).model_dump_json(),
            qos=1,
        )

    async def pause_simulation(self):
        await self._mqtt_client.publish(
            PauseMessage.topic(), PauseMessage().model_dump_json(), qos=1
        )

    async def step_simulation(self, seconds: float):
        await self._mqtt_client.publish(
            StepMessage.topic(),
            StepMessage(seconds=seconds).model_dump_json(),
            qos=1,
        )

    async def set_automation(self, enabled: bool):
        await self._mqtt_client.publish(
            SetAutomationMessage.topic(),
            SetAutomationMessage(enabled=enabled).model_dump_json(),
            qos=1,
        )

    def wait_for_simulation_status(
        self,
        status: Literal["stepping", "running", "available"],
        *_args,
        timeout: float,
    ) -> Coroutine[None, None, SimulationStatusMessage]:
        return self._simulation_status.wait_for(lambda s: s.status == status, timeout)

    def wait_for_control_status(
        self, automatic: bool, *_args, timeout: float
    ) -> Coroutine[None, None, ControlStatusMessage]:
        return self._control_status.wait_for(
            lambda s: s.automatic == automatic, timeout
        )

    def _parse_message[T: ThrsModel](self, message: Message, model: type[T]) -> T:
        if not isinstance(message.payload, str | bytes):
            raise ValueError(f"Expected string or bytes, got {type(message.payload)}")
        return model.model_validate_json(message.payload)

    @property
    def simulation_status(self) -> SimulationStatusMessage | None:
        return self._simulation_status.last

    @property
    def control_status(self) -> ControlStatusMessage | None:
        return self._control_status.last
