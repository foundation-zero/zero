from .adapter import PCanAdapter
from .config import Settings
from .stub import PCanStub

from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)
from .logging import setup_logging
import logging

setup_logging()

logger = logging.getLogger("cli")


class AdapterCmd(Settings):
    async def cli_cmd(self) -> None:
        logger.info("Running adapter...")
        async with PCanAdapter.init_from_settings(self) as adapter:
            await adapter.run()


class StubCmd(Settings):
    async def cli_cmd(self) -> None:
        logger.info("Running stub...")
        async with PCanStub.init_from_settings(self) as adapter:
            await adapter.run()


class ZeroLoadsAdapter(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    adapter: CliSubCommand[AdapterCmd]
    stub: CliSubCommand[StubCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
