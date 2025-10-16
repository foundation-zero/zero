import logging

import uvicorn
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)

from loads.api.auth import generate_jwt
from loads.config import Settings
from loads.control import PCanAdapter, PCanStub, SensorStub
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


class PCanStubCmd(Settings):
    async def cli_cmd(self) -> None:
        logger.info("Running pcan stub...")
        async with PCanStub.init_from_settings(self) as stub:
            await stub.run()


class SensorStubCmd(Settings):
    async def cli_cmd(self) -> None:
        logger.info("Running sensor stub...")
        async with SensorStub.init_from_settings(self) as stub:
            await stub.run()


class ControlCli(Settings):
    async def cli_cmd(self):
        logger.info("Running control...")
        async with LoadsControl.init_from_settings(self) as control:
            run_task = await control.run()
            await run_task


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
    pcan_stub: CliSubCommand[PCanStubCmd]
    sensor_stub: CliSubCommand[SensorStubCmd]
    control: CliSubCommand[ControlCli]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
