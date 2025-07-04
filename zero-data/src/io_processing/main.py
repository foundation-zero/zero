import logging
import sys

from io_processing.dbt_gen import generate_dbt
from io_processing.data_gen import generate_data
from argparse import ArgumentParser


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        stream=sys.stdout,
    )


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
    setup_logging()
    args = parser().parse_args()
    args.func()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
