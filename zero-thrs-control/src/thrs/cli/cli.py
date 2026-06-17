import logging

from pydantic_settings import (BaseSettings, CliApp, CliSubCommand,
                               SettingsConfigDict)
from thrs.cli.config.modes import CommConnectorMode, RunnerMode, SimulationMode
from thrs.cli.runner.runnables.control import ControlRunnable
from thrs.cli.runner.runnables.simulation import SimulationRunnable
from thrs.cli.runner.runner import Runnable, Runner
from thrs.orchestration.config import Config
from thrs.orchestration.config_logging import setup_logging
from thrs.orchestration.connectors.connector import CommConnector
from thrs.orchestration.connectors.connector_factory import get_connector

setup_logging()

logger: logging.Logger = logging.getLogger(__name__)


class LockstepCmd(Config):
    simulation_mode: SimulationMode
    communication_mode: CommConnectorMode = CommConnectorMode.MEMORY

    async def cli_cmd(self) -> None:
        logger.info("Running THRS Lockstep...")
        logger.info(f"Simulation mode: {self.simulation_mode}")
        logger.info(f"Communication mode: {self.communication_mode}")

        comm_connector: CommConnector = get_connector(self, self.communication_mode)

        # Runnables, due to lockstep; always 1 simulation and 1 control
        simulation = SimulationRunnable(
            simulation_mode=self.simulation_mode,
            topic_base="/simulation/..",
            comm_connector=comm_connector,
        )
        control = ControlRunnable(
            name="control", topic_base="/control", comm_connector=comm_connector
        )
        runnables: list[Runnable] = [simulation, control]

        runner = Runner(
            runnables=runnables, runner_mode=RunnerMode.LOCKSTEP
        )  # TODO: Implement synced Directives
        await runner.run()


class SimulatorCmd(Config):
    simulation_mode: list[SimulationMode]

    async def cli_cmd(self) -> None:
        logger.info("Running THRS Simulator...")
        logger.info(f"Simulation mode: {self.simulation_mode}")

        comm_connector: CommConnector = get_connector(self, CommConnectorMode.MQTT)

        runnables: list[Runnable] = []

        for mode in self.simulation_mode:
            simulation = SimulationRunnable(
                simulation_mode=mode,
                topic_base="/simulation/..",
                comm_connector=comm_connector,
            )
            runnables.append(simulation)

        runner = Runner(runnables=runnables)

        await runner.run()


class ControlCmd(Config):
    async def cli_cmd(self) -> None:
        logger.info("Running THRS control...")

        comm_connector: CommConnector = get_connector(self, CommConnectorMode.MQTT)
        control = ControlRunnable(
            name="control", topic_base="/control", comm_connector=comm_connector
        )

        runnables: list[Runnable] = [control]
        runner = Runner(runnables=runnables)

        await runner.run()


class THRS_cli(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    lockstep: CliSubCommand[LockstepCmd]
    simulator: CliSubCommand[SimulatorCmd]
    control: CliSubCommand[ControlCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
        CliApp.run_subcommand(self)
