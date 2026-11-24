import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated

from aiomqtt import Client as MqttClient
from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliImplicitFlag,
    CliPositionalArg,
    CliSubCommand,
    SettingsConfigDict,
)

from thrs.cli.log import setup_logging
from thrs.cli.setup import (
    setup_control_modules,
    setup_database,
    setup_persistence_manager,
    setup_simulation_module,
)
from thrs.orchestration.comms import DirectivesChannels, MqttConnector
from thrs.orchestration.config import Config
from thrs.orchestration.module import Module
from thrs.orchestration.simulation import SimulationUnit
from thrs.runtime.descriptions.simulation import ModeName, lookup_mode
from thrs.runtime.directives import DirectiveHandling
from thrs.runtime.liveness import Liveness
from thrs.runtime.loop import ControllableLoop, RealtimeLoop
from thrs.runtime.runners.control import ControlRunner
from thrs.runtime.runners.lockstep import LockstepRunner
from thrs.runtime.runners.simulator import SimulationRunner
from thrs.runtime.runtime import Runtime

logger: logging.Logger = logging.getLogger(__name__)


class ControlCmd(BaseSettings):
    mode: ModeName
    module_persistence: CliImplicitFlag[bool] = True
    allow_boot_without_persistence_having_active_postgres: CliImplicitFlag[bool] = False

    async def cli_cmd(self) -> None:
        logger.debug("Starting control command: %s", self.mode)
        settings = Config()

        liveness_check = Liveness(settings.liveness_path)

        control_mode = lookup_mode(self.mode)

        database = setup_database(settings, self.module_persistence)

        persistence = await setup_persistence_manager(
            database,
            self.module_persistence,
            self.allow_boot_without_persistence_having_active_postgres,
        )

        async with MqttClient(
            settings.mqtt_host,
            settings.mqtt_port,
            identifier=settings.mqtt_control_client_id,
            username=settings.mqtt_username,
            password=settings.mqtt_password,
        ) as mqtt_client:
            connector = MqttConnector(mqtt_client)

            control_modules: list[Module] = await setup_control_modules(
                connector,
                settings,
                control_mode.control_modules,
                datetime.now,
                persistence,
            )

            runner = ControlRunner(control_modules, liveness_check, persistence)
            runtime = Runtime(RealtimeLoop(), runner, connector)

            logger.info("Running control")

            await runtime.start()


class SimulationCmd(BaseSettings):
    mode: ModeName

    async def cli_cmd(self) -> None:
        logger.debug("Starting simulation command: %s", self.mode)
        settings = Config()

        liveness_check = Liveness(settings.liveness_path)

        simulation_mode = lookup_mode(self.mode)

        async with MqttClient(
            settings.mqtt_host,
            settings.mqtt_port,
            identifier=settings.mqtt_simulation_client_id,
            username=settings.mqtt_username,
            password=settings.mqtt_password,
        ) as mqtt_client:
            connector = MqttConnector(mqtt_client=mqtt_client)

            if simulation_mode.simulation_description is None:
                raise ValueError("simulation must be defined for simulation mode")

            simulation_module: SimulationUnit = setup_simulation_module(
                connector,
                settings,
                simulation_mode.control_modules,
                simulation_mode.simulation_description,
            )

            runner = SimulationRunner(simulation_module, liveness_check)
            runtime = Runtime(RealtimeLoop(), runner, connector)

            logger.info("Running simulation")
            await runtime.start()


class LockstepCmd(BaseSettings):
    mode: ModeName
    play: CliImplicitFlag[bool] = False
    module_persistence: CliImplicitFlag[bool] = True
    allow_boot_without_persistence_having_active_postgres: CliImplicitFlag[bool] = False

    async def setup(self, settings: Config, mqtt_client: MqttClient) -> Runtime:
        logger.debug("Starting lockstep command: %s", self.mode)
        mode = lookup_mode(self.mode)

        connector = MqttConnector(mqtt_client)

        if mode.simulation_description is None:
            raise ValueError(
                f"Simulation must be defined for lockstep mode. Chosen mode '{self.mode}' has no simulation description."
            )

        simulation_module: SimulationUnit = setup_simulation_module(
            connector,
            settings,
            mode.control_modules,
            mode.simulation_description,
        )

        database = setup_database(settings, self.module_persistence)

        persistence = await setup_persistence_manager(
            database,
            self.module_persistence,
            self.allow_boot_without_persistence_having_active_postgres,
        )

        control_modules: list[Module] = await setup_control_modules(
            connector,
            settings,
            mode.control_modules,
            time_fn=simulation_module.time,
            persistence=persistence,
            # Lockstep trades delivery guarantees for speed; every tick republishes these values
            publish_qos=0,
        )

        runner = LockstepRunner(control_modules, simulation_module, persistence)

        directives_channels = DirectivesChannels(connector, settings)
        directive_handling = DirectiveHandling(
            directives_channels,
            mode,
            simulation_module.time,
        )
        loop = ControllableLoop(
            simulation_module.tick_duration, simulation_module.time, directive_handling
        )
        await loop.clear_previous()
        if self.play:
            await loop.play()
        return Runtime(loop, runner, connector)

    async def cli_cmd(self) -> None:
        settings = Config()

        async with (
            MqttClient(
                settings.mqtt_host,
                settings.mqtt_port,
                identifier=settings.mqtt_lockstep_client_id,
                username=settings.mqtt_username,
                password=settings.mqtt_password,
            ) as mqtt_client,
        ):
            runtime = await self.setup(settings, mqtt_client)
            logger.info("Running lockstep")

            await runtime.start()


class AsyncApiCmd(BaseModel):
    """Generate the THRS AsyncAPI document."""

    output_file: Annotated[
        CliPositionalArg[str], Field(description="File to store the resulting asyncapi")
    ]

    def cli_cmd(self) -> None:
        # Spec generation walks every module description; keep it off the
        # import path of the runtime commands.
        from thrs.spec.asyncapi import generate_asyncapi  # noqa: PLC0415

        # Hardcoded because we can't really change them on the places where it matters
        settings = Config(
            mqtt_host="",
            mqtt_port=0,
            mqtt_devices_topic_prefix="marpower",
            mqtt_controller_topic_prefix="thrs/controller",
            mqtt_controller_topic_suffix="set",
            mqtt_simulator_topic_prefix="thrs/simulator",
            mqtt_simulator_topic_suffix="set",
            mqtt_control_topic_suffix="Command",
        )
        thrs_mode = lookup_mode("thrs")

        spec = generate_asyncapi(settings, thrs_mode)

        with Path(self.output_file).open("w") as result_file:
            result_file.write(spec.model_dump_json(indent=2, by_alias=True))


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
    generate_asyncapi: CliSubCommand[AsyncApiCmd]

    def cli_cmd(self) -> None:
        setup_logging()

        CliApp.run_subcommand(self)
