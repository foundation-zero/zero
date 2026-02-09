import logging
import os
import sys

from pydantic_settings import (
    CliApp,
    CliPositionalArg,
    CliSubCommand,
    SettingsConfigDict,
)

from thrs.cli.control import run_all
from thrs.cli.simulation_controls import Modes, SimulationControls
from thrs.orchestration.config import Config

logger = logging.getLogger("cli")


def setup_logging():
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        stream=sys.stdout,
    )


class RunCli(Config):
    """Run a simulation process for a single module"""

    type: CliPositionalArg[Modes]

    async def cli_cmd(self) -> None:
        logger.info(f"Running {self.type} simulation...")
        async with SimulationControls.from_settings(self) as controls:
            await controls.clear_previous()
            await controls.run(self.type)


class ControlCli(Config):
    """Run the control modules"""

    async def cli_cmd(self) -> None:
        logger.info("Running control modules...")
        await run_all()


class SimulateCli(Config):
    """Run simulation process for all modules"""

    async def cli_cmd(self) -> None:
        logger.info("Simulate command not yet implemented")


class THRS(Config, cli_kebab_case=True):
    """THRS (Thermal Harvesting & Recovery System) CLI"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    run: CliSubCommand[RunCli]
    control: CliSubCommand[ControlCli]
    simulate: CliSubCommand[SimulateCli]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)


if __name__ == "__main__":
    setup_logging()
    CliApp.run(THRS)
