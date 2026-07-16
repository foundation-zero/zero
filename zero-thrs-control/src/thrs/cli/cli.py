import logging
from datetime import datetime, timedelta

from aiomqtt import Client as MqttClient
from pydantic_settings import BaseSettings, CliApp, CliSubCommand, SettingsConfigDict

from thrs.orchestration.comms import DirectivesChannels, MqttConnector
from thrs.orchestration.config import Config
from thrs.orchestration.log import setup_logging
from thrs.orchestration.setup import setup_control_modules, setup_simulation_module
from thrs.runtime.descriptions.simulation import ModeName, lookup_mode
from thrs.runtime.directives import DirectiveHandling
from thrs.runtime.liveness import Liveness
from thrs.runtime.runners.control import ControlRunner
from thrs.runtime.runners.lockstep import LockstepRunner
from thrs.runtime.runners.simulator import SimulationRunner
from thrs.runtime.runtime import Runtime

logger: logging.Logger = logging.getLogger(__name__)


class ControlCmd(BaseSettings):
    mode: ModeName

    async def cli_cmd(self) -> None:
        settings = Config()  # type: ignore

        liveness_check = Liveness(settings.liveness_path)

        control_mode = lookup_mode(self.mode)
        async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
            connector = MqttConnector(mqtt_client)

            control_modules = setup_control_modules(
                connector,
                settings,
                control_mode.control_modules,
                datetime.now,
            )
            runner = ControlRunner(control_modules, liveness_check)
            runtime = Runtime(runner, connector, timedelta(seconds=1))

            await runtime.loop.play(1)
            logger.info("Running control")
            await runtime.start()


class SimulationCmd(BaseSettings):
    mode: ModeName

    async def cli_cmd(self) -> None:
        settings = Config()  # type: ignore

        liveness_check = Liveness(settings.liveness_path)

        simulation_mode = lookup_mode(self.mode)
        async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
            connector = MqttConnector(mqtt_client=mqtt_client)

            if simulation_mode.simulation_description is None:
                raise ValueError("simulation must be defined for simulation mode")

            simulation_module = setup_simulation_module(
                connector,
                settings,
                simulation_mode.control_modules,
                simulation_mode.simulation_description,
            )

            runner = SimulationRunner(simulation_module, liveness_check)
            runtime = Runtime(runner, connector, simulation_module.tick_duration)

            await runtime.loop.play(1)
            logger.info("Running simulation")
            await runtime.start()


class LockstepCmd(BaseSettings):
    mode: ModeName

    def setup(self, settings: Config, mqtt_client: MqttClient) -> Runtime:
        mode = lookup_mode(self.mode)

        connector = MqttConnector(mqtt_client)

        if mode.simulation_description is None:
            raise ValueError("simulation must be defined for lockstep mode")

        simulation_module = setup_simulation_module(
            connector,
            settings,
            mode.control_modules,
            mode.simulation_description,
        )

        control_modules = setup_control_modules(
            connector,
            settings,
            mode.control_modules,
            time_fn=simulation_module.time,
        )

        runner = LockstepRunner(control_modules, simulation_module)

        directives_channels = DirectivesChannels(connector, settings)

        directive_handling = DirectiveHandling(
            directives_channels,
            mode,
            simulation_module.time,
        )
        return Runtime(
            runner,
            connector,
            simulation_module.tick_duration,
            directive_handling,
        )

    async def cli_cmd(self) -> None:
        settings = Config()  # type: ignore

        async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
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
