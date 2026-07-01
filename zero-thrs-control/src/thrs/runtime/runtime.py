from asyncio import TaskGroup, sleep
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncGenerator

from aiomqtt import Client as MqttClient

from thrs.input_output.base import CombinedValues
from thrs.orchestration.config import Config
from thrs.orchestration.connector import MqttConnector
from thrs.orchestration.module import CombinedControl
from thrs.runtime.descriptions.simulation import MODES, Mode, Modes
from thrs.runtime.directives import DirectiveHandling
from thrs.runtime.loop import EMPTY_HOOKS, Loop
from thrs.runtime.messages import Messaging
from thrs.runtime.runners import ControlRunner, LockstepRunner, Runner, SimulationRunner


class Runtime:
    def __init__(
        self,
        runner: Runner,
        tick_duration: timedelta,
        directive_handling: DirectiveHandling | None = None,
        connectors: list[MqttConnector] | None = None,
    ):
        self._loop = Loop(tick_duration)
        self._runner = runner
        self._directive_handling = directive_handling
        self._connectors = connectors or []

    @staticmethod
    def _lookup_mode(mode: Modes) -> Mode:
        return next((m for m in MODES if m.name == mode))

    @asynccontextmanager
    @staticmethod
    async def setup_for_simulation(
        config: Config, selected_mode: Modes
    ) -> "AsyncGenerator[Runtime, None]":
        mode = Runtime._lookup_mode(selected_mode)
        simulation = mode.setup_simulation()
        if simulation is None:
            raise ValueError("simulation must be defined for simulation mode")
        async with MqttClient(config.mqtt_host, config.mqtt_port) as simulation_client:
            connector = MqttConnector(
                simulation_client,
                config.mqtt_devices_topic_prefix,
                config.mqtt_controller_topic_prefix,
                sensor_values_clss={},  # simulation gets sensor values from the simulation
                control_values_clss=mode.control_module.control_values_clss,
                controller_state_clss={},
                simulation_outputs_clss=simulation.outputs_cls,
                sensor_topic_suffix=config.mqtt_control_topic_suffix,
            )
            yield Runtime(
                SimulationRunner(connector, simulation),
                simulation.tick_duration,
                connectors=[connector],
            )

    @asynccontextmanager
    @staticmethod
    async def setup_for_lockstep(
        config: Config, selected_mode: Modes
    ) -> "AsyncGenerator[Runtime, None]":
        mode = Runtime._lookup_mode(selected_mode)
        simulation = mode.setup_simulation()
        if simulation is None:
            raise ValueError("simulation must be defined for lockstep mode")
        async with (
            MqttClient(config.mqtt_host, config.mqtt_port) as directive_client,
            MqttClient(config.mqtt_host, config.mqtt_port) as simulation_client,
            MqttClient(config.mqtt_host, config.mqtt_port) as control_client,
        ):
            control_connector = MqttConnector(
                mqtt_client=control_client,
                devices_topic_prefix=config.mqtt_devices_topic_prefix,
                controller_topic_prefix=config.mqtt_controller_topic_prefix,
                sensor_values_clss=mode.control_module.sensor_values_clss,
                control_values_clss=mode.control_module.control_values_clss,
                controller_state_clss={},  # Nothing yet, but we want to send controller values here at some point
                control_topic_suffix=config.mqtt_control_topic_suffix,
            )

            parameters = {
                module: mode.control_module.parameters_for_module(module)()
                for module in mode.control_module.modules
            }

            control: CombinedControl = mode.control_module.control(
                CombinedValues(parameters), simulation.time
            )

            simulation_connector = MqttConnector(
                mqtt_client=simulation_client,
                devices_topic_prefix=config.mqtt_devices_topic_prefix,
                controller_topic_prefix=config.mqtt_controller_topic_prefix,
                sensor_values_clss={},  # simulation gets sensor values from the simulation
                control_values_clss=mode.control_module.control_values_clss,
                controller_state_clss={},
                simulation_outputs_clss=simulation.outputs_cls,
                sensor_topic_suffix=config.mqtt_control_topic_suffix,
            )
            runner = LockstepRunner(
                control=control,
                control_connector=control_connector,
                simulation_module_name=mode.name,
                simulation=simulation,
                simulation_connector=simulation_connector,
                alarms=mode.control_module.alarms(),
            )

            directive_handling = DirectiveHandling(
                Messaging(directive_client),
                mode,
                simulation.time,
                config.mqtt_controller_topic_prefix,
            )
            yield Runtime(
                runner,
                simulation.tick_duration,
                directive_handling,
                connectors=[control_connector, simulation_connector],
            )

    @asynccontextmanager
    @staticmethod
    async def setup_for_control(
        config: Config, selected_mode: Modes
    ) -> "AsyncGenerator[Runtime, None]":
        mode = Runtime._lookup_mode(selected_mode)
        async with MqttClient(config.mqtt_host, config.mqtt_port) as control_client:
            control_connector = MqttConnector(
                mqtt_client=control_client,
                devices_topic_prefix=config.mqtt_devices_topic_prefix,
                controller_topic_prefix=config.mqtt_controller_topic_prefix,
                sensor_values_clss=mode.control_module.sensor_values_clss,
                control_values_clss=mode.control_module.control_values_clss,
                controller_state_clss={},  # Nothing yet, but we want to send controller values here at some point
                control_topic_suffix=config.mqtt_control_topic_suffix,
            )

            parameters = {
                module: mode.control_module.parameters_for_module(module)()
                for module in mode.control_module.modules
            }

            control = mode.control_module.control(
                CombinedValues(parameters), datetime.now
            )
            runner = ControlRunner(
                control=control,
                connector=control_connector,
                alarms=mode.control_module.alarms(),
            )
            yield Runtime(runner, timedelta(seconds=1), connectors=[control_connector])

    async def start(self):
        async with TaskGroup() as tg:
            for connector in self._connectors:
                tg.create_task(connector.run())

            # await sleep(
            #     0.1
            # )  # Wait a bit for the connectors to be ready before starting the runner and directive handling
            if self._directive_handling is not None:
                await self._directive_handling.handler(self._loop).register()
                tg.create_task(self._directive_handling.run())
            hooks = (
                self._directive_handling.hooks()
                if self._directive_handling is not None
                else EMPTY_HOOKS
            )
            tg.create_task(
                self._loop.loop(
                    self._runner,
                    hooks,
                )
            )

    async def clear_previous(self):
        if self._directive_handling is not None:
            await self._directive_handling.clear_previous()

    @property
    def loop(self) -> Loop:
        return self._loop
