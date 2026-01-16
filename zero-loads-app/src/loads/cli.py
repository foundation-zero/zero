import logging

import uvicorn
from generator import DataGenerator
from generator.config import Settings as GeneratorSettings
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)

from loads.api.auth import generate_jwt
from loads.config import Settings
from loads.control import ConditionsStub, Control, PCanAdapter, PCanStub
from loads.logging_config import setup_logging
from loads.sensors.messaging import at_sensors, plc_sensors

setup_logging()

logger = logging.getLogger("cli")


class ApiCli(Settings):
    async def cli_cmd(self) -> None:
        logger.info("Running API...")
        uvicorn.run("loads.api.api:app", host="0.0.0.0", port=5101, reload=True)


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


class ConditionsStubCmd(Settings):
    async def cli_cmd(self) -> None:
        logger.info("Running conditions stub...")
        async with ConditionsStub.init_from_settings(self) as stub:
            await stub.run()


class ControlCli(Settings):
    async def cli_cmd(self) -> None:
        logger.info("Running control...")
        async with Control.init_from_settings(self) as control:
            run_task = await control.run()
            await run_task


class PlcSensorsStubCmd(GeneratorSettings):
    async def cli_cmd(self) -> None:
        logger.info("Running plc sensors stub...")
        async with DataGenerator.init_from_settings(
            self, "plc_sensors_stub_generator"
        ) as data_gen:
            config = plc_sensors.gen_config()
            await data_gen.generate(config=config)


class ATSensorsStubCmd(GeneratorSettings):
    async def cli_cmd(self) -> None:
        logger.info("Running A+T sensors stub...")
        async with DataGenerator.init_from_settings(
            self, "at_sensors_stub_generator"
        ) as data_gen:
            config = at_sensors.gen_config()
            await data_gen.generate(config=config)


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
    conditions_stub: CliSubCommand[ConditionsStubCmd]
    control: CliSubCommand[ControlCli]
    plc_sensors_stub: CliSubCommand[PlcSensorsStubCmd]
    at_sensors_stub: CliSubCommand[ATSensorsStubCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
