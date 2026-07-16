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
    MqttConnector,
)
from thrs.orchestration.config import Config
from thrs.orchestration.log import setup_logging
from thrs.orchestration.setup import setup_control, setup_lockstep, setup_simulation
from thrs.runtime.descriptions.simulation import ModeNames, lookup_mode
from thrs.runtime.runners.control import ControlRunner
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

            runner_args = setup_control(connector, settings, control_mode, datetime.now)
            runner = ControlRunner(*runner_args)
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

    async def cli_cmd(self) -> None:
        settings = Config()  # type: ignore
        mode = lookup_mode(self.mode)

        async with (
            MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client,
        ):
            runtime = setup_lockstep(mode, settings, mqtt_client)
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
