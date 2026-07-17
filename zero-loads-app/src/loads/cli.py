import logging
from pathlib import Path

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
from loads.control import ConditionsStub, Control
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
            config for module in ensure_list(modules) for config in module.gen_config()
        ]
        await data_gen.generate(config=configs)


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

        logger.info(
            f"Running sensor stubs, using the following modules: {', '.join(module.display_name for module in messaging_modules)}..."
        )

        await _run_data_generator(self, "all_sensors_stub_generator", messaging_modules)


class ExportSeedCmd(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    input: Path = Path("src/sailpack")
    output: Path = Path("../hasura/seeds/zero/loads_reference_values.sql")

    async def cli_cmd(self) -> None:
        from sailpack.export_seed import export_seed_sql

        logger.info("Exporting sailpack seed SQL...")
        load_case_count, reference_count = export_seed_sql(self.input, self.output)
        logger.info(
            f"Generated {self.output} with {load_case_count} load cases and "
            f"{reference_count} reference values."
        )


class ZeroLoads(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    api: CliSubCommand[ApiCli]
    generate_jwt: CliSubCommand[GenerateJWT]
    conditions_stub: CliSubCommand[ConditionsStubCmd]
    control: CliSubCommand[ControlCli]
    at_sensors_stub: CliSubCommand[ATSensorsStubCmd]
    fiber_optic_sensors_stub: CliSubCommand[FiberOpticSensorsStubCmd]
    sail_system_sensors_stub: CliSubCommand[SailSystemSensorsStubCmd]
    sensors_stub: CliSubCommand[SensorsStubCmd]
    export_seed: CliSubCommand[ExportSeedCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
