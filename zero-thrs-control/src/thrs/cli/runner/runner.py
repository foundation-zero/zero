import asyncio
import logging
import math
import time

from thrs.cli.config.modes import RunnerMode, SimulationMode
from thrs.cli.runner.runnables.runnable import Runnable


class Runner:
    def __init__(
        self, runnables: list[Runnable], runner_mode: RunnerMode = RunnerMode.NORMAL
    ):
        self.guard_if_lockstep(runnables, runner_mode)

        self.runnables = runnables
        self.runner_mode = runner_mode
        self.logger = logging.getLogger(__name__)

    def log_loaded_runnables(self):
        for runnable in self.runnables:
            self.logger.info(
                f"Loaded runnable: {runnable.name} with topic base: {runnable.topic_base}"
            )

    # Run all runnables in sequence, respect the tickrate of each runnable.
    async def run(self):
        self.logger.info(f"Running with mode:{self.runner_mode}")

        # A tick consist of executing these per runnable:
        #  1. Retrieving parameters and sensor/command values
        #  2. Running the tick function
        #  3. Sending the command/sensor values to the respective broker topics
        #
        # Therefore, the run loop needs to be structured in a way that allows for this.
        # In lockstep mode, the tick of each runnable should be executed sequentially. While in normal mode, they are executed in parallel.

        while True:
            # Keep track of time, to take in account time required to perform tick(s)
            start: float = time.monotonic()

            for runnable in self.runnables:
                if runnable.paused:
                    continue

                # Since lockstep requires a synchronized tick with the control,
                # The runnable is ticked successively instead of letting runnable tick itself multiple times at once.
                tick_rate: int = math.ceil(runnable.tick_rate)
                for _ in range(int(tick_rate)):
                    runnable.tick()

            elapsed: float = time.monotonic() - start
            sleep: float = max(0, 1.0 - elapsed)
            await asyncio.sleep(sleep)

    # In lockstep mode, ensure that there are exactly 2 runnables and that one is a simulation and the other is control.
    def guard_if_lockstep(self, runnables, runner_mode):
        if runner_mode == RunnerMode.LOCKSTEP:
            if len(runnables) != 2:
                raise ValueError("Lockstep mode requires exactly 2 runnables")

            sim_count = sum(
                isinstance(getattr(r, "simulation_mode", None), SimulationMode)
                for r in runnables
            )
            if sim_count != 1:
                raise ValueError(
                    "Lockstep mode requires exactly one simulation runnable and one control runnable"
                )
