from argparse import ArgumentParser

from thrs.cli.simulation_controls import (
    MODES,
    SimulationControls,
)
from thrs.orchestration.config import Config


settings = Config()  # type: ignore


async def main():
    parser = ArgumentParser("THRS")

    subparser = parser.add_subparsers()

    run_cmd = subparser.add_parser("run", help="Run the THRS simulation and control")
    run_cmd.add_argument(
        "type",
        choices=MODES.keys(),
        type=lambda val: val.upper(),
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
        await controls.run(args.type)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
