import logging
import os
import sys
from argparse import ArgumentParser

from thrs.cli.simulation_controls import (
    MODES,
    SimulationControls,
)
from thrs.orchestration.config import Config


def setup_logging():
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        stream=sys.stdout,
    )


settings = Config()  # type: ignore


async def main():
    setup_logging()
    parser = ArgumentParser("THRS")

    subparser = parser.add_subparsers()

    run_cmd = subparser.add_parser("run", help="Run the THRS simulation and control")
    run_cmd.add_argument(
        "type",
        choices=MODES.keys(),
        help="Type of simulation to run",
    )
    run_cmd.set_defaults(func=run)

    args = parser.parse_args()
    if hasattr(args, "func"):
        await args.func(args)
    else:
        parser.print_help()


async def run(args):
    async with SimulationControls.from_settings(settings) as controls:
        await controls.clear_previous()
        await controls.run(args.type)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
