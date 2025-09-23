import logging

import uvicorn
from loads.config import Settings
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)

from loads.api.auth import generate_jwt
from loads.control import PCanAdapter, PCanStub
from loads.logging import setup_logging
from .control import LoadsControl

setup_logging()

logger = logging.getLogger("cli")


class ApiCli(Settings):
    async def cli_cmd(self) -> None:
        logger.info("Running API...")
        uvicorn.run("loads.api.api:app", reload=True)


class GenerateJWT(Settings):
    roles: str

    async def cli_cmd(self) -> None:
        await generate_jwt(self)


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


class ControlCli(Settings):
    async def cli_cmd(self):
        logger.info("Running control...")
        async with LoadsControl.init_from_settings(self) as control:
            await control.run()


class ZeroLoads(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    api: CliSubCommand[ApiCli]
    generate_jwt: CliSubCommand[GenerateJWT]
    adapter: CliSubCommand[AdapterCmd]
    stub: CliSubCommand[StubCmd]
    control: CliSubCommand[ControlCli]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
