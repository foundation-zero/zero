from .config import Settings
from .auth import generate_jwt

from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)
import uvicorn


class ApiCli(Settings):
    async def cli_cmd(self) -> None:
        uvicorn.run("api.api:app", reload=True)


class GenerateJWT(Settings):
    roles: str

    async def cli_cmd(self) -> None:
        await generate_jwt(self)


class ZeroLoads(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    api: CliSubCommand[ApiCli]
    generate_jwt: CliSubCommand[GenerateJWT]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
