from argparse import ArgumentParser
import asyncio
from textwrap import dedent
from typing import Any, Callable

from polars import DataFrame
from yaml import dump

from io_processing.components import Components
from io_processing.data_gen.gen import Generator, Strategy
from io_processing.io_list import IoFlavor, normalize_io_list
from io_processing.marpower import read_excel


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
    components_parser = sub_parser.add_parser(
        "components", help="commands regarding components"
    )
    components_sub_parser = components_parser.add_subparsers(title="component commands")
    components_describe = components_sub_parser.add_parser(
        "describe", help="combine components with io"
    )
    components_describe.set_defaults(func=adapt(describe))

    signals_parser = sub_parser.add_parser("signals", help="commands regarding signals")
    signals_sub_parser = signals_parser.add_subparsers(title="signals")
    signals_list_units = signals_sub_parser.add_parser(
        "list-units", help="list units found in signals"
    )
    signals_list_units.set_defaults(func=adapt(list_units))
    signals_list_orphans = signals_sub_parser.add_parser(
        "list-orphans", help="list signals without component"
    )
    signals_list_orphans.set_defaults(func=adapt(list_orphaned_signals))
    signals_generate = signals_sub_parser.add_parser("generate", help="generate values")
    signals_generate.set_defaults(func=adapt(generate))

    return parser


def adapt(fn: Callable[[DataFrame, Components], Any]):
    def _act():
        df = read_excel("ios/52422003_3210_AMCS IO-List R1.11.xlsx")
        io_list = normalize_io_list(df, IoFlavor.AMCS)
        components = Components("./components.yaml")

        result = fn(io_list, components)
        print(dump(result, sort_keys=False))

    return _act


def run():
    args = parser().parse_args()
    args.func()


def describe(io_list: DataFrame, components: Components):
    return components.combine_io(io_list, IoFlavor.AMCS).to_dicts()


def list_units(io_list: DataFrame, components):
    io_list["unit"].to_list()


def list_orphaned_signals(io_list: DataFrame, components: Components):
    return components.orphan_signals(io_list).to_dicts()


def generate(io_list: DataFrame, components: Components):
    genny = Generator(
        components.combine_io(io_list, IoFlavor.AMCS),
        components._description,
        IoFlavor.AMCS,
    )
    asyncio.run(genny.run(Strategy.ZERO))


if __name__ == "__main__":
    run()
