import logging
import sys

from pydantic import BaseModel
from pydantic_settings import BaseSettings, CliApp, CliSubCommand

from zero_data.dbt_gen import generate_dbt
from zero_data.data_gen import generate_data


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        stream=sys.stdout,
    )


class GenerateDataCmd(BaseModel):
    """Generate values"""

    def cli_cmd(self):
        generate_data()


class GenerateDbtCmd(BaseModel):
    """Generate all dbt resources"""

    def cli_cmd(self):
        generate_dbt()


class ZeroDataCli(BaseSettings, cli_kebab_case=True):
    """Zero Data

    Zero Data is able to ingest various flavors of IO list (Marpower, Vitters)
    and combine it with a component list to output a description of the components
    of that system.

    Furthermore it is able to process those inputs into the RisingWave source and
    materialized views which can be synced to a dbt.
    """

    generate_data: CliSubCommand[GenerateDataCmd]
    generate_dbt: CliSubCommand[GenerateDbtCmd]

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
