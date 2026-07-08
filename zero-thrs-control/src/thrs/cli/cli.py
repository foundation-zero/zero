import logging
from datetime import datetime, timedelta

from aiomqtt import Client as MqttClient
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)

from thrs.orchestration.comms import (
    DirectivesChannels,
    MqttConnector,
)
from thrs.orchestration.config import Config
from thrs.orchestration.log import setup_logging
from thrs.orchestration.setup import setup_control, setup_simulation
from thrs.runtime.descriptions.simulation import ModeNames, lookup_mode
from thrs.runtime.directives import DirectiveHandling
from thrs.runtime.runners.control import ControlRunner
from thrs.runtime.runners.lockstep import LockstepRunner
from thrs.runtime.runners.simulator import SimulationRunner
from thrs.runtime.runtime import Runtime

logger: logging.Logger = logging.getLogger(__name__)


class ControlCmd(BaseSettings):
    mode: ModeNames

    async def cli_cmd(self) -> None:
        settings = Config()  # type: ignore

        control_mode = lookup_mode(self.mode)
        async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
            connector = MqttConnector(mqtt_client)

            control_channels = setup_control(connector, settings, control_mode)
            runner = ControlRunner(
                control_mode.control_modules, datetime.now, control_channels
            )
            runtime = Runtime(runner, connector, timedelta(seconds=1))

            await runtime.loop.play(1)
            logger.info("Running control")
            await runtime.start()


class SimulationCmd(BaseSettings):
    mode: ModeNames

    async def cli_cmd(self) -> None:
        settings = Config()  # type: ignore

        simulation_mode = lookup_mode(self.mode)
        async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
            connector = MqttConnector(mqtt_client=mqtt_client)

            simulation, channels = setup_simulation(
                connector, settings, simulation_mode
            )
            runner = SimulationRunner(simulation, channels)
            runtime = Runtime(runner, connector, simulation.tick_duration)

            await runtime.loop.play(1)
            logger.info("Running simulation")
            await runtime.start()


class LockstepCmd(BaseSettings):
    mode: ModeNames

    def setup(self, settings: Config, mqtt_client: MqttClient) -> Runtime:
        mode = lookup_mode(self.mode)

        connector = MqttConnector(mqtt_client)

        simulation, simulation_channels = setup_simulation(connector, settings, mode)

        control_channels = setup_control(connector, settings, mode)

        runner = LockstepRunner(
            control_modules=mode.control_modules,
            time_fn=simulation.time,
            control_channels=control_channels,
            simulation=simulation,
            simulation_channels=simulation_channels,
        )

        directives_channels = DirectivesChannels(connector, settings)

        directive_handling = DirectiveHandling(
            directives_channels,
            mode,
            simulation.time,
        )
        return Runtime(
            runner,
            connector,
            simulation.tick_duration,
            directive_handling,
        )

    async def cli_cmd(self) -> None:
        settings = Config()  # type: ignore

        async with (
            MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client,
        ):
            runtime = self.setup(settings, mqtt_client)
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
