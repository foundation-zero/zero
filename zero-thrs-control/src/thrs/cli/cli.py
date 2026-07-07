import logging
from datetime import datetime, timedelta
from typing import Callable

from aiomqtt import Client as MqttClient
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)

from thrs.input_output.base import CombinedValues
from thrs.orchestration.comms import (
    ControlChannels,
    DirectivesChannels,
    MqttConnector,
    SimulationChannels,
)
from thrs.orchestration.config import Config
from thrs.orchestration.log import setup_logging
from thrs.orchestration.module import CombinedAlarms, CombinedControl
from thrs.orchestration.simulation import Simulation
from thrs.runtime.descriptions.simulation import MODES, Mode, Modes
from thrs.runtime.directives import DirectiveHandling
from thrs.runtime.runners.control import ControlRunner
from thrs.runtime.runners.lockstep import LockstepRunner
from thrs.runtime.runners.simulator import SimulationRunner
from thrs.runtime.runtime import Runtime

logger: logging.Logger = logging.getLogger(__name__)
settings = Config()  # type: ignore


def lookup_mode(mode: Modes) -> Mode:
    return next((m for m in MODES if m.name == mode))


def setup_simulation(
    connector: MqttConnector, config: Config, mode: Mode
) -> tuple[SimulationChannels, Simulation]:
    simulation = mode.setup_simulation()
    if simulation is None:
        raise ValueError("simulation must be defined for simulation mode")

    return (
        SimulationChannels(
            connector,
            config,
            mode.control_module.sensor_values_clss,
            mode.control_module.control_values_clss,
            simulation.inputs_cls,
            simulation.outputs_cls,
        ),
        simulation,
    )


def setup_control(
    connector: MqttConnector,
    config: Config,
    mode: Mode,
    time_fn: Callable[[], datetime],
) -> tuple[ControlChannels, CombinedControl, CombinedAlarms]:
    control_channels = ControlChannels(connector, config, mode.control_module)

    parameters = {
        module: mode.control_module.parameters_for_module(module)()
        for module in mode.control_module.modules
    }

    control = mode.control_module.control(CombinedValues(parameters), time_fn)

    return control_channels, control, mode.control_module.alarms()


class ControlCmd(Config):
    modes: Modes

    async def cli_cmd(self) -> None:
        mode = lookup_mode(self.modes)
        async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
            connector = MqttConnector(mqtt_client)

            runner_args = setup_control(connector, settings, mode, datetime.now)
            runner = ControlRunner(*runner_args)
            runtime = Runtime(runner, connector, timedelta(seconds=1))

            await runtime.loop.play(1)
            logger.info("Running control")
            await runtime.start()


class SimulationCmd(Config):
    modes: Modes

    async def cli_cmd(self) -> None:
        mode = lookup_mode(self.modes)

        async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
            connector = MqttConnector(mqtt_client=mqtt_client)

            channels, simulation = setup_simulation(connector, settings, mode)
            runner = SimulationRunner(channels, simulation)
            runtime = Runtime(runner, connector, simulation.tick_duration)

            await runtime.loop.play(1)
            logger.info("Running simulation")
            await runtime.start()


class LockstepCmd(Config):
    modes: Modes

    async def cli_cmd(self) -> None:
        mode = lookup_mode(self.modes)
        async with (
            MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client,
        ):
            connector = MqttConnector(mqtt_client)

            simulation_channels, simulation = setup_simulation(
                connector, settings, mode
            )

            control_channels, control, alarms = setup_control(
                connector, settings, mode, simulation.time
            )

            runner = LockstepRunner(
                control=control,
                control_channels=control_channels,
                simulation=simulation,
                simulation_channels=simulation_channels,
                alarms=alarms,
            )

            directives_channels = DirectivesChannels(connector, settings)

            directive_handling = DirectiveHandling(
                directives_channels,
                mode,
                simulation.time,
            )
            runtime = Runtime(
                runner,
                connector,
                simulation.tick_duration,
                directive_handling,
            )

            await runtime.clear_previous()
            logger.info("Running lockstep")
            await runtime.start()


class ThrsCli(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    lockstep: CliSubCommand[LockstepCmd]
    simulation: CliSubCommand[SimulationCmd]
    control: CliSubCommand[ControlCmd]

    def cli_cmd(self) -> None:
        setup_logging()

        try:
            CliApp.run_subcommand(self)
        except KeyboardInterrupt:
            pass
