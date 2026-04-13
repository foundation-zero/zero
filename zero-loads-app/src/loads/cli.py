import logging

import uvicorn
from generator import DataGenerator
from generator.base import GeneratorConfig
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
from loads.registry import (
    MessagingModule,
    at_sensors,
    fiber_optic_sensors,
    sail_system_sensors,
)
from loads.util import ensure_list

setup_logging()

logger: logging.Logger = logging.getLogger("cli")


class ApiCli(Settings):
    async def cli_cmd(self) -> None:
        logger.info("Running API...")
        uvicorn.run(
            "loads.api.api:app", host="0.0.0.0", port=5101, reload=self.is_development
        )


class GenerateJWT(Settings):
    roles: str
    jwt_secret: str

    async def cli_cmd(self) -> None:
        await generate_jwt(self, roles=self.roles, jwt_secret=self.jwt_secret)


class AdapterCmd(Settings):
    canbus_ip: str
    canbus_port: int
    canbus_buffer_size: int

    async def cli_cmd(self) -> None:
        logger.info("Running adapter...")
        async with PCanAdapter.init_from_settings(
            self,
            canbus_ip=self.canbus_ip,
            canbus_port=self.canbus_port,
            canbus_buffer_size=self.canbus_buffer_size,
        ) as adapter:
            await adapter.run()


class PCanStubCmd(Settings):
    canbus_ip: str
    canbus_port: int
    canbus_buffer_size: int

    async def cli_cmd(self) -> None:
        logger.info("Running pcan stub...")
        async with PCanStub.init_from_settings(
            self,
            canbus_ip=self.canbus_ip,
            canbus_port=self.canbus_port,
            canbus_buffer_size=self.canbus_buffer_size,
        ) as stub:
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


async def _run_data_generator(
    settings: GeneratorSettings,
    id: str,
    modules: list[MessagingModule] | MessagingModule,
):
    async with DataGenerator.init_from_settings(settings, id) as data_gen:
        configs: list[GeneratorConfig] = [
          config
          for module in ensure_list(modules)
          for config in module
        ]
        await data_gen.generate(config=config)


class SailSystemSensorsStubCmd(GeneratorSettings):
    async def cli_cmd(self) -> None:
        logger.info("Running sail system sensors stub...")
        await _run_data_generator(
            self, "sail_system_sensors_stub_generator", sail_system_sensors
        )


class ATSensorsStubCmd(GeneratorSettings):
    async def cli_cmd(self) -> None:
        logger.info("Running A+T sensors stub...")
        await _run_data_generator(self, "at_sensors_stub_generator", at_sensors)


class FiberOpticSensorsStubCmd(GeneratorSettings):
    async def cli_cmd(self) -> None:
        logger.info("Running fiber optic sensors stub...")
        await _run_data_generator(
            self, "fiber_optic_sensors_stub_generator", fiber_optic_sensors
        )


class SensorsStubCmd(GeneratorSettings):
    async def cli_cmd(self) -> None:
        messaging_modules: list[MessagingModule] = [
            sail_system_sensors,
            at_sensors,
            fiber_optic_sensors,
        ]

        messaging_module_names = ", ".join(
            module.display_name for module in messaging_modules
        )

        logger.info(
            f"Running all sensor stubs, using the following modules: {messaging_module_names}..."
        )

        await _run_data_generator(self, "all_sensors_stub_generator", messaging_modules)


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
    at_sensors_stub: CliSubCommand[ATSensorsStubCmd]
    fiber_optic_sensors_stub: CliSubCommand[FiberOpticSensorsStubCmd]
    sail_system_sensors_stub: CliSubCommand[SailSystemSensorsStubCmd]
    sensors_stub: CliSubCommand[SensorsStubCMD]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
