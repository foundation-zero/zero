import logging
import os
import sys

import asyncclick as click
from asyncclick import BadParameter

from thrs.cli.simulation_controls import (
    SimulationControls,
    MODES,
)
from thrs.orchestration.config import Config


def setup_logging():
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        stream=sys.stdout,
    )


settings = Config()  # type: ignore


@click.group
async def main():
    setup_logging()


@main.command()
async def simulate():
    """Run simulation process for all the modules"""


@main.command()
async def control():
    """Run the control modules"""


@main.command()
@click.argument("type")
async def run(type):
    """Run a simulation process for a single module"""
    if type not in MODES:
        raise BadParameter(f"TYPE must be one of {','.join(MODES.keys())}")
    async with SimulationControls.from_settings(settings) as controls:
        await controls.clear_previous()
        await controls.run(type)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
