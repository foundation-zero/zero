from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)
from loads.config import Settings
from .api.auth import generate_jwt
from .control import PCanAdapter, PCanStub
from .logging import setup_logging
import logging
import uvicorn

setup_logging()

logger = logging.getLogger("cli")


class ApiCli(Settings):
    async def cli_cmd(self) -> None:
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

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
