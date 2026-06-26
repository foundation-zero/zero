import logging

from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliPositionalArg,
    CliSubCommand,
    SettingsConfigDict,
)

from thrs.cli.simulation_controls import (
    Modes,
    SimulationControls,
)
from thrs.orchestration.config import Config
from thrs.orchestration.log import setup_logging

logger: logging.Logger = logging.getLogger(__name__)
settings = Config()  # type: ignore


class RunCmd(Config):
    mode: CliPositionalArg[
        Modes
    ]  # For now, keep it as previous structure, but we can change it to a subcommand in the future.

    async def cli_cmd(self) -> None:
        async with SimulationControls.from_settings(settings) as controls:
            await controls.clear_previous()
            await controls.run(self.mode)


class ThrsCli(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    run: CliSubCommand[RunCmd]

    def cli_cmd(self) -> None:
        setup_logging()
        try:
            CliApp.run_subcommand(self)
        except KeyboardInterrupt:
            pass
