import logging

import jwt
import uvicorn
from pydantic_settings import (
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)

from domestic_control.config import settings, Settings
from domestic_control.logging import setup_logging

setup_logging()

logger = logging.getLogger("cli")


class ApiCli(Settings):
    async def cli_cmd(self) -> None:
        logger.info("Running API...")
        uvicorn.run("domestic_control.app:app", host="0.0.0.0", port=5100, reload=True)


class GenerateJWT(Settings):
    roles: list[str] = []
    cabin: str | None = None

    async def cli_cmd(self) -> None:
        SUPPORTED_ROLES = {"user", "admin"}
        unique_roles = set(["user"] + self.roles)
        roles = list(unique_roles)

        if unsupported_roles := (unique_roles - SUPPORTED_ROLES):
            raise ValueError(
                f"Roles {unsupported_roles} are not supported. Supported roles are: {', '.join(SUPPORTED_ROLES)}"
            )

        claims = {
            "x-hasura-default-role": "user",
            "x-hasura-allowed-roles": roles,
        }

        if self.cabin:
            claims["x-hasura-cabin"] = self.cabin

        token = jwt.encode(
            {"https://hasura.io/jwt/claims": claims},
            settings.jwt_secret,
            algorithm="HS256",
        )
        print(f"JWT for roles ({', '.join(roles)}): {token}")


class ControlCli(Settings):
    async def cli_cmd(self) -> None:
        from domestic_control.control import Control

        logger.info("Running control...")
        async with Control.init_from_settings(settings) as control:
            await control.run()


class StubCli(Settings):
    async def cli_cmd(self) -> None:
        from domestic_control.services.stubs import Stub

        logger.info("Running stub...")
        async with Stub.from_settings(settings) as stub:
            await stub.run()


class DomesticControl(Settings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    api: CliSubCommand[ApiCli]
    generate_jwt: CliSubCommand[GenerateJWT]
    control: CliSubCommand[ControlCli]
    stub: CliSubCommand[StubCli]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
