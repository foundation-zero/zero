import logging

from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)

from thrs.orchestration.config import Config
from thrs.orchestration.log import setup_logging
from thrs.runtime.descriptions.simulation import Modes
from thrs.runtime.runtime import Runtime

logger: logging.Logger = logging.getLogger(__name__)
settings = Config()  # type: ignore


class ControlCmd(Config):
    mode: Modes

    async def cli_cmd(self) -> None:
        async with Runtime.setup_for_control(settings, self.mode) as runtime:
            await runtime.start()
            await runtime.loop.play(1)


class SimulatorCmd(Config):
    mode: Modes

    async def cli_cmd(self) -> None:
        async with Runtime.setup_for_simulation(settings, self.mode) as runtime:
            await runtime.start()
            await runtime.loop.play(1)


class LockstepCmd(Config):
    mode: Modes

    async def cli_cmd(self) -> None:
        async with Runtime.setup_for_lockstep(settings, self.mode) as runtime:
            await runtime.clear_previous()
            await runtime.start()


class ThrsCli(BaseSettings, cli_kebab_case=True):
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
        setup_logging()
        logger.debug("Running THRS control...")

        try:
            CliApp.run_subcommand(self)
        except KeyboardInterrupt:
            pass
