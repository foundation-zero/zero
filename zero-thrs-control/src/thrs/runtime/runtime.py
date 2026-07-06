from asyncio import TaskGroup
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncGenerator, Coroutine

from aiomqtt import Client as MqttClient

from thrs.input_output.base import CombinedValues
from thrs.orchestration.comms import (
    ControlChannels,
    DirectivesChannels,
    MqttConnector,
    SimulationChannels,
)
from thrs.orchestration.config import Config
from thrs.orchestration.module import CombinedControl
from thrs.runtime.descriptions.simulation import MODES, Mode, Modes
from thrs.runtime.directives import DirectiveHandling
from thrs.runtime.loop import EMPTY_HOOKS, Loop
from thrs.runtime.runners import (
    ControlRunner,
    LockstepRunner,
    Runner,
    SimulationRunner,
)


class Runtime:
    def __init__(
        self,
        runner: Runner,
        tick_duration: timedelta,
        directive_handling: DirectiveHandling | None = None,
        connector_runs: list[Coroutine[None, None, None]] | None = None,
    ):
        self._loop = Loop(tick_duration)
        self._runner = runner
        self._directive_handling = directive_handling
        self._connectors = connector_runs or []

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
            connector = MqttConnector(mqtt_client=simulation_client)

            channels = SimulationChannels(
                connector,
                config,
                mode.control_module.sensor_values_clss,
                mode.control_module.control_values_clss,
                simulation.inputs_cls,
                simulation.outputs_cls,
            )
            yield Runtime(
                SimulationRunner(channels, simulation),
                simulation.tick_duration,
                connector_runs=[await connector.run()],
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
            control_connector = MqttConnector(control_client)
            control_channels = ControlChannels(
                control_connector,
                config,
                mode.control_module,
            )

            parameters = {
                module: mode.control_module.parameters_for_module(module)()
                for module in mode.control_module.modules
            }

            control: CombinedControl = mode.control_module.control(
                CombinedValues(parameters), simulation.time
            )

            simulation_connector = MqttConnector(simulation_client)
            simulation_channels = SimulationChannels(
                simulation_connector,
                config,
                mode.control_module.sensor_values_clss,
                mode.control_module.control_values_clss,
                simulation.inputs_cls,
                simulation.outputs_cls,
            )
            runner = LockstepRunner(
                control=control,
                control_channels=control_channels,
                simulation_module_name=mode.name,
                simulation=simulation,
                simulation_channels=simulation_channels,
                alarms=mode.control_module.alarms(),
            )

            directive_connector = MqttConnector(directive_client)

            directives_channels = DirectivesChannels(directive_connector, config)

            directive_handling = DirectiveHandling(
                directives_channels,
                mode,
                simulation.time,
            )
            yield Runtime(
                runner,
                simulation.tick_duration,
                directive_handling,
                connector_runs=[
                    await control_connector.run(),
                    await simulation_connector.run(),
                    await directive_connector.run(),
                ],
            )

    @asynccontextmanager
    @staticmethod
    async def setup_for_control(
        config: Config, selected_mode: Modes
    ) -> "AsyncGenerator[Runtime, None]":
        mode = Runtime._lookup_mode(selected_mode)
        async with MqttClient(config.mqtt_host, config.mqtt_port) as control_client:
            connector = MqttConnector(control_client)
            control_channels = ControlChannels(connector, config, mode.control_module)

            parameters = {
                module: mode.control_module.parameters_for_module(module)()
                for module in mode.control_module.modules
            }

            control = mode.control_module.control(
                CombinedValues(parameters), datetime.now
            )
            runner = ControlRunner(
                channels=control_channels,
                control=control,
                alarms=mode.control_module.alarms(),
            )
            yield Runtime(
                runner, timedelta(seconds=1), connector_runs=[await connector.run()]
            )

    async def start(self):
        """Start the runtime, including the loop and any directive handling if present. Hooks are used to send status messages for directive handling."""
        async with TaskGroup() as tg:
            for connector in self._connectors:
                tg.create_task(connector)

            if self._directive_handling is not None:
                await self._directive_handling.handler(self._loop).register()

            status_hooks = (
                self._directive_handling.status_hooks()
                if self._directive_handling is not None
                else EMPTY_HOOKS
            )

            tg.create_task(
                self._loop.loop(
                    self._runner,
                    status_hooks,
                )
            )

    async def clear_previous(self):
        if self._directive_handling is not None:
            await self._directive_handling.clear_previous()

    @property
    def loop(self) -> Loop:
        return self._loop
