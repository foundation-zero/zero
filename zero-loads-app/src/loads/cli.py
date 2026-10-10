import logging
import sys
import tempfile
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
from loads.registry.sheets import TABS, TabName, consistency_problems, download_tab
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


class SeedPaths(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    input: Path = Path("src/sailpack/load_cases")
    sailpack_mapping: Path = TABS["sailpack-mapping"].path
    max_loads: Path = TABS["max-loads"].path
    reference_values_output: Path = Path(
        "../hasura/seeds/zero/loads_reference_values.sql"
    )
    target_threshold_conflicts_output: Path = Path(
        "src/sailpack/target_threshold_conflicts.csv"
    )
    load_case_mapping_output: Path = Path(
        "../hasura/seeds/zero/loads_case_mappings.sql"
    )


class ExportSeedCmd(SeedPaths):
    async def cli_cmd(self) -> None:
        from sailpack.export_load_case_mapping_seed import (
            export_load_case_mapping_seed_sql,
        )
        from sailpack.export_reference_values_seed import (
            export_reference_values_seed_sql,
        )

        logger.info("Exporting sailpack seed SQL...")
        load_case_count, reference_count, conflict_count = (
            export_reference_values_seed_sql(
                input_source=self.input,
                mapping_path=self.sailpack_mapping,
                max_loads_path=self.max_loads,
                output_sql=self.reference_values_output,
                conflicts_output=self.target_threshold_conflicts_output,
            )
        )
        logger.info(
            f"Generated {self.reference_values_output} with {load_case_count} load cases and "
            f"{reference_count} reference values."
        )
        if conflict_count:
            logger.warning(
                f"Dropped {conflict_count} targets above their warning or alarm threshold, "
                f"see {self.target_threshold_conflicts_output}."
            )

        load_case_mapping_count, _ = export_load_case_mapping_seed_sql(
            input_source=self.input, output_sql=self.load_case_mapping_output
        )
        logger.info(
            f"Generated {self.load_case_mapping_output} with {load_case_mapping_count} load case mappings."
        )


def _stale_seed_files(paths: SeedPaths) -> list[Path]:
    from sailpack.export_load_case_mapping_seed import (
        export_load_case_mapping_seed_sql,
    )
    from sailpack.export_reference_values_seed import (
        export_reference_values_seed_sql,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        generated_reference_values = temp_path / paths.reference_values_output.name
        generated_case_mappings = temp_path / paths.load_case_mapping_output.name
        generated_conflicts = temp_path / paths.target_threshold_conflicts_output.name

        export_reference_values_seed_sql(
            input_source=paths.input,
            mapping_path=paths.sailpack_mapping,
            max_loads_path=paths.max_loads,
            output_sql=generated_reference_values,
            conflicts_output=generated_conflicts,
        )
        export_load_case_mapping_seed_sql(
            input_source=paths.input, output_sql=generated_case_mappings
        )

        return [
            committed
            for committed, generated in (
                (paths.reference_values_output, generated_reference_values),
                (paths.load_case_mapping_output, generated_case_mappings),
                (paths.target_threshold_conflicts_output, generated_conflicts),
            )
            if committed.read_bytes() != generated.read_bytes()
        ]


def _log_stale_seed_files(stale: list[Path]) -> None:
    for path in stale:
        logger.error(f"Seed file is out of date: {path}")
    logger.error(
        "Run 'uv run loads export-seed' from zero-loads-app to regenerate the seed files."
    )


class CheckSeedCmd(SeedPaths):
    async def cli_cmd(self) -> None:
        if stale := _stale_seed_files(self):
            _log_stale_seed_files(stale)
            sys.exit(1)

        logger.info("Seed files are consistent with the sailpack export.")


class DownloadSheetsCmd(SeedPaths):
    tabs: list[TabName] = list(TABS)

    async def cli_cmd(self) -> None:
        for tab_name in self.tabs:
            tab = TABS[tab_name]
            download_tab(tab)
            logger.info(f"Downloaded {tab_name} to {tab.path}")

        if problems := consistency_problems():
            for problem in problems:
                logger.error(problem)
            sys.exit(1)
        logger.info("Sheet exports are consistent with the registry.")

        if stale := _stale_seed_files(self):
            _log_stale_seed_files(stale)
            sys.exit(1)
        logger.info("Seed files are consistent with the sheet exports.")


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
    download_sheets: CliSubCommand[DownloadSheetsCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
