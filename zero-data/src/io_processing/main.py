from argparse import ArgumentParser
import asyncio
from pathlib import Path

from io_processing.config import MQTTConfig
from io_processing.data_gen.gen import Generator
from io_processing.generator.all import generate
from io_processing.io_list.marpower import read_amcs_excel_to_io_topics


def parser():
    parser = ArgumentParser(
        prog="io-processing",
        description="""
      IO processing is able to ingest various flavors of IO list (Marpower, Vitters)
      and combine it with a component list to output a description of the components
      of that system.

      Furthermore it is able to process those inputs into the RisingWave source and 
      materialized views which can be synced to a dbt.
    """,
    )
    sub_parser = parser.add_subparsers(title="commands")
    signals_generate = sub_parser.add_parser("generate-data", help="generate values")
    signals_generate.set_defaults(func=generate_data)

    generate_parser = sub_parser.add_parser(
        "generate-dbt", help="generate all dbt resources"
    )
    generate_parser.set_defaults(func=generate_dbt)

    return parser


def run():
    args = parser().parse_args()
    args.func()


def generate_dbt():
    return generate()


def generate_data():
    repo_root = Path(__file__).parent / "../.."
    topics = read_amcs_excel_to_io_topics(
        repo_root / "io_lists/52422003_3210_AMCS IO-List R1.11.xlsx"
    )

    mqtt_config = MQTTConfig()
    genny = Generator(10, mqtt_config, topics)
    asyncio.run(genny.run())


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
