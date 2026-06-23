import logging

from pydantic_settings import BaseSettings, CliApp, CliSubCommand, SettingsConfigDict

from src.thrs.cli.runner.runnables.control_runnable import ControlRunnable
from src.thrs.cli.runner.runnables.simulation_runnable import SimulationRunnable
from thrs.cli.config.modes import (
    CLIRunnerMode,
    CommConnectorMode,
    ControlMode,
    SimulationMode,
)
from thrs.cli.runner.runnables.runnable import Runnable
from thrs.cli.runner.runner import Runner
from thrs.orchestration.config import Config
from thrs.orchestration.config_logging import setup_logging
from thrs.orchestration.connectors.base import CommConnector
from thrs.orchestration.connectors.data_definitions import (
    control_module_definitions,
    simulation_module_definitions,
)

setup_logging()

logger: logging.Logger = logging.getLogger(__name__)


class LockstepCmd(Config):
    simulation_mode: SimulationMode
    control_modes: list[ControlMode] = list(ControlMode)
    communication_mode: CommConnectorMode = CommConnectorMode.MEMORY
    minimal_time_between_tick_iterations: float = 1.0

    async def cli_cmd(self) -> None:
        logger.info("Running THRS Lockstep...")
        logger.info(f"Simulation mode: {self.simulation_mode.value}")
        logger.info(
            f"Control modes: {[control_mode.value for control_mode in self.control_modes]}"
        )
        logger.info(f"Communication mode: {self.communication_mode}")

        async with CommConnector.create(
            self, self.communication_mode
        ) as comm_connector:
            # Due to lockstep; always 1 simulation
            runnables: list[Runnable] = []

            # Get definition based on mode
            simulation = await SimulationRunnable.create(
                comm_connector=comm_connector,
                simulation_definition=simulation_module_definitions[
                    self.simulation_mode
                ],
                minimal_time_between_tick_iterations=self.minimal_time_between_tick_iterations,
            )
            runnables.append(simulation)

            runnables: list[Runnable] = []
            for control_mode in self.control_modes:
                control = await ControlRunnable.create(
                    comm_connector=comm_connector,
                    control_module_definition=control_module_definitions[control_mode],
                    minimal_time_between_tick_iterations=self.minimal_time_between_tick_iterations,
                )

                runnables.append(control)

            runner = Runner(
                runnables=runnables, runner_mode=CLIRunnerMode.LOCKSTEP
            )  # TODO: Implement synced Directives
            await runner.run()


class SimulatorsCmd(Config):
    simulation_modes: list[SimulationMode]
    minimal_time_between_tick_iterations: float = 1.0
    communication_mode: CommConnectorMode = CommConnectorMode.MQTT

    async def cli_cmd(self) -> None:
        logger.info("Running THRS Simulator(s)...")
        logger.info(
            f"Simulation mode: {', '.join(x.name for x in self.simulation_modes)}"
        )

        async with CommConnector.create(
            self, self.communication_mode
        ) as comm_connector:
            runnables: list[Runnable] = []

            for simulation_mode in self.simulation_modes:
                simulation = await SimulationRunnable.create(
                    comm_connector=comm_connector,
                    simulation_definition=simulation_module_definitions[
                        simulation_mode
                    ],
                    minimal_time_between_tick_iterations=self.minimal_time_between_tick_iterations,
                )

                runnables.append(simulation)

            runner = Runner(runnables=runnables)

            await runner.run()


class ControlCmd(Config):
    control_modes: list[ControlMode] = list(ControlMode)
    minimal_time_between_tick_iterations: float = 1.0
    communication_mode: CommConnectorMode = CommConnectorMode.MQTT

    async def cli_cmd(self) -> None:
        logger.info("Running THRS control...")
        logger.info(
            f"Control modes: {[control_mode.value for control_mode in self.control_modes]}"
        )

        async with CommConnector.create(
            self, self.communication_mode
        ) as comm_connector:
            runnables: list[Runnable] = []
            for control_mode in self.control_modes:
                control = await ControlRunnable.create(
                    comm_connector=comm_connector,
                    control_module_definition=control_module_definitions[control_mode],
                    minimal_time_between_tick_iterations=self.minimal_time_between_tick_iterations,
                )

                runnables.append(control)

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
    simulators: CliSubCommand[SimulatorsCmd]
    control: CliSubCommand[ControlCmd]

    def cli_cmd(self) -> None:
        try:
            CliApp.run_subcommand(self)
        except KeyboardInterrupt:
            pass
