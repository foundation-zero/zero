import logging
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

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

# The seed code needs dev dependencies that the Docker image does not install.
if TYPE_CHECKING:
    from loads.registry.sheets import LoadsSheet
    from sailpack.export_seed import SeedExport

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


class SeedPaths(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    input: Path = Path("src/sailpack/load_cases")
    seed_output: Path = Path("../hasura/seeds/zero/loads.sql")
    target_threshold_conflicts_output: Path = Path(
        "src/sailpack/target_threshold_conflicts.csv"
    )


def _download_consistent_sheet() -> "LoadsSheet":
    from loads.registry.sheets import LoadsSheet, consistency_problems

    sheet = LoadsSheet.download()
    if problems := consistency_problems(sheet):
        for problem in problems:
            logger.error(problem)
        sys.exit(1)
    logger.info("The loads sheet is consistent with the registry.")
    return sheet


def _export_seed(
    paths: SeedPaths,
    sheet: "LoadsSheet",
    seed_output: Path,
    target_threshold_conflicts_output: Path,
) -> "SeedExport":
    from sailpack.export_seed import export_seed_sql

    return export_seed_sql(
        input_source=paths.input,
        mapping_csv=sheet.sailpack_mapping,
        max_loads_csv=sheet.max_loads,
        output_sql=seed_output,
        conflicts_output=target_threshold_conflicts_output,
    )


class ExportSeedCmd(SeedPaths):
    async def cli_cmd(self) -> None:
        sheet = _download_consistent_sheet()

        logger.info("Exporting sailpack seed SQL...")
        export = _export_seed(
            self, sheet, self.seed_output, self.target_threshold_conflicts_output
        )
        logger.info(
            f"Generated {self.seed_output} with {export.load_case_count} load cases, "
            f"{export.reference_count} reference values and "
            f"{export.load_case_mapping_count} load case mappings."
        )
        if export.conflict_count:
            logger.warning(
                f"Clamped {export.conflict_count} targets outside their warning or alarm thresholds, "
                f"see {self.target_threshold_conflicts_output}."
            )
        for ambiguous in export.ambiguous_load_cases:
            lower, upper = ambiguous.aws_range
            aws_range = f"{lower:g}–{upper:g}" if upper is not None else f"{lower:g}+"
            logger.warning(
                f"Load cases {ambiguous.load_case_ids} share the sail set "
                f"{'+'.join(ambiguous.sail_abbreviations)}, the {ambiguous.awa_range_id} AWA range "
                f"and the AWS range {aws_range} kn; "
                f"only {ambiguous.load_case_ids[0]} is mapped there."
            )


def _stale_seed_files(paths: SeedPaths, sheet: "LoadsSheet") -> list[Path]:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        generated_seed = temp_path / paths.seed_output.name
        generated_conflicts = temp_path / paths.target_threshold_conflicts_output.name

        _export_seed(paths, sheet, generated_seed, generated_conflicts)

        return [
            committed
            for committed, generated in (
                (paths.seed_output, generated_seed),
                (paths.target_threshold_conflicts_output, generated_conflicts),
            )
            if committed.read_bytes() != generated.read_bytes()
        ]


class CheckSeedCmd(SeedPaths):
    async def cli_cmd(self) -> None:
        sheet = _download_consistent_sheet()

        if stale := _stale_seed_files(self, sheet):
            for path in stale:
                logger.error(f"Seed file is out of date: {path}")
            logger.error(
                "Run 'uv run loads export-seed' from zero-loads-app to regenerate the seed files."
            )
            sys.exit(1)

        logger.info(
            "Seed files are consistent with the loads sheet and the sailpack export."
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
    check_seed: CliSubCommand[CheckSeedCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
