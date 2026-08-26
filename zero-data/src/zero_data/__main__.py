import logging
import sys
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, CliApp, CliSubCommand

from zero_data.data_gen import generate_data
from zero_data.vector_gen import generate_vector


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        stream=sys.stdout,
    )


class GenerateDataCmd(BaseModel):
    """Generate values"""

    cache_dir: Annotated[
        str | None, Field(description="Directory to cache IO list results")
    ] = None

    exclude_io_lists: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="IO list names to exclude (repeat option for multiple names)",
        ),
    ]

    def cli_cmd(self):
        generate_data(
            excluded_io_list_names=self.exclude_io_lists,
            cache_dir=Path(self.cache_dir) if self.cache_dir else None,
        )


class GenerateVectorCmd(BaseModel):
    """Generate all vector resources"""

    cache_dir: Annotated[
        str | None, Field(description="Directory to cache IO list results")
    ] = None

    def cli_cmd(self):
        generate_vector(Path(self.cache_dir) if self.cache_dir else None)


class ZeroDataCli(BaseSettings, cli_kebab_case=True):
    """Zero Data

    Zero Data is able to ingest various flavors of IO list (Marpower, Vitters)
    and combine it with a component list to output a description of the components
    of that system.

    Furthermore it is able to process those inputs into the RisingWave source and
    materialized views which can be synced to a dbt.
    """

    generate_data: CliSubCommand[GenerateDataCmd]
    generate_vector: CliSubCommand[GenerateVectorCmd]

    def cli_cmd(self):
        CliApp.run_subcommand(self)


def run():
    setup_logging()
    CliApp.run(ZeroDataCli)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
