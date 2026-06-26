from asyncio import (
    FIRST_COMPLETED,
    Queue,
    TaskGroup,
    create_task,
    sleep,
    wait,
)
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Callable, Coroutine, Never, assert_never, cast
from aiomqtt import Client as MqttClient

from thrs.orchestration.config import Config
from thrs.orchestration.runner import Runner
from thrs.messaging.definition import MessagingDefinition, MessageRouter
from thrs.runtime.lockstep import router as lockstep_router
from thrs.runtime.control import router as control_router
from thrs.runtime.simulation import router as simulation_router


@dataclass
class MqttTopicConfig:
    devices_topic_prefix: str
    runtime_topic_prefix: str
    simulation_topic_prefix: str
    control_topic_suffix: str

    @staticmethod
    def from_settings(settings: Config) -> "MqttTopicConfig":
        return MqttTopicConfig(
            devices_topic_prefix=settings.mqtt_devices_topic_prefix,
            runtime_topic_prefix=settings.mqtt_controller_topic_prefix,
            simulation_topic_prefix=settings.mqtt_simulation_topic_prefix,
            control_topic_suffix=settings.mqtt_control_topic_suffix,
        )


def construct_definition(config: MqttTopicConfig) -> MessagingDefinition:
    definition = MessagingDefinition()
    definition.delegate(config.simulation_topic_prefix, lockstep_router)
    definition.delegate(config.simulation_topic_prefix, simulation_router)
    # This is possibly a bit of a mismatch, but at the same time having the bit handling the control messages being called control within runtime does makes a bit of sense
    definition.delegate(config.runtime_topic_prefix, control_router)
    return definition


class Runtime:
    def __init__(
        self,
        runtime_client: MqttClient,
        control_client: MqttClient,
        sensor_client: MqttClient,
        topic_config: MqttTopicConfig,
    ):
        self._runtime_client = runtime_client
        self._control_client = control_client
        self._sensor_client = sensor_client
        self._topic_config = topic_config

        self._definition = construct_definition(topic_config)
        # TODO: receive initialized simulation/control ready to run
        # TODO: construct loop with correct hooks (publishing simulation status message) for current environment

    async def run(self):
        await self._definition.subscribe(self._runtime_client)
        # TODO: run loop

    @staticmethod
    @asynccontextmanager
    async def from_settings(settings: Config):
        async with (
            MqttClient(settings.mqtt_host, settings.mqtt_port) as controls_client,
            MqttClient(settings.mqtt_host, settings.mqtt_port) as control_client,
            MqttClient(settings.mqtt_host, settings.mqtt_port) as sensor_client,
        ):
            yield Runtime(
                runtime_client=controls_client,
                control_client=control_client,
                sensor_client=sensor_client,
                topic_config=MqttTopicConfig.from_settings(settings),
            )


@dataclass
class First[T]:
    result: T


@dataclass
class Second[T]:
    result: T


type Hook = Callable[["Loop"], None]


@dataclass
class LoopHooks:
    available: Hook
    running: Hook
    stepping: Hook


EMPTY_HOOKS = LoopHooks(lambda _: None, lambda _: None, lambda _: None)


class Loop:
    def __init__(self, hooks=EMPTY_HOOKS):
        self._playing = False
        self._playback_rate = 1.0
        self._pauses = Queue()
        self._plays: Queue[float] = Queue()
        self._steps: Queue[int] = Queue()
        self._hooks = hooks

    async def loop(self, runner: Runner):
        while True:
            self._hooks.available(self)
            result = await self.wait_either(self._plays.get(), self._steps.get())
            match result:
                case First(playback_rate):
                    self._playing = True
                    self._playback_rate = playback_rate
                    self._hooks.running(self)
                    while self._pauses.empty():
                        async with TaskGroup() as tg:
                            tg.create_task(sleep(1))
                            tg.create_task(runner.run(1))
                    self._pauses.get_nowait()
                    self._playing = False
                case Second(steps):
                    self._hooks.stepping(self)
                    await runner.run(steps)

    async def play(self, playback_rate: float):
        await self._plays.put(playback_rate)

    async def pause(self):
        await self._pauses.put(None)

    async def step(self, ticks: int):
        await self._steps.put(ticks)

    @staticmethod
    async def wait_either[A, B](
        a: Coroutine[None, None, A], b: Coroutine[None, None, B]
    ) -> First[A] | Second[B]:
        a_task, b_task = create_task(a), create_task(b)
        dones, _waiting = await wait([a_task, b_task], return_when=FIRST_COMPLETED)
        result = dones.pop()
        if result == a_task:
            return First(a_task.result())
        elif result == b_task:
            return Second(b_task.result())
        else:
            assert_never(
                cast(Never, result)
            )  # Type checker isn't smart enough to know that result == a_task matches all Task[A]s (or same for result == b_task)
