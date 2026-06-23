from __future__ import annotations

import asyncio
import logging
import math
import time
from typing import TYPE_CHECKING

from src.thrs.cli.runner.runnables.simulation_runnable import SimulationResult

if TYPE_CHECKING:
    from thrs.cli.config.modes import CLIRunnerMode, SimulationMode
    from thrs.cli.runner.runnables.runnable import Runnable


class Runner:
    def __init__(
        self,
        runnables: list["Runnable"],
        runner_mode: "CLIRunnerMode" = "CLIRunnerMode.NORMAL",
        minimal_time_between_tick_iterations: float = 1.0,
    ):
        self.logger = logging.getLogger(__name__)

        self.guard(runnables, runner_mode)

        self.runner_mode = runner_mode
        self.minimal_time_between_tick_iterations = minimal_time_between_tick_iterations
        print(f"all runnables: {[(r.__class__.__name__) for r in runnables]}")

        # Store runnables in Simulation and Control separate
        self._runnables = runnables
        self.split_ctrl_sim_runnable_types()

    def split_ctrl_sim_runnable_types(self):
        from src.thrs.cli.runner.runnables.control_runnable import (
            ControlRunnable,  # TODO Maapater: fix circular import
        )
        from src.thrs.cli.runner.runnables.simulation_runnable import (
            SimulationRunnable,  # TODO Maapater: fix circular import
        )

        """ Split the runnables into simulation and control runnables, to be able to tick them separately. """
        self._runnable_sims = [
            x for x in self._runnables if isinstance(x, SimulationRunnable)
        ]
        self._runnable_controls = [
            x for x in self._runnables if isinstance(x, ControlRunnable)
        ]

    def log_loaded_runnables(self):
        for runnable in self._runnables:
            self.logger.info(
                f"Loaded runnable: {runnable.name} with topic base: {runnable.topic_base}"
            )

    async def run(self):
        """Run all simulations in sequence first and control successively, respecting the tickrate of each runnable."""
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
            start_time: float = time.monotonic()

            self.run_simulation_runnables()
            self.run_control_runnables()

            await self.ensure_minimal_time_per_tick_iteration(start_time)

    async def ensure_minimal_time_per_tick_iteration(self, start_time: float):
        """Ensure that the time between tick iterations is at least the minimal time specified, to avoid out of sync ticks."""
        elapsed: float = time.monotonic() - start_time
        sleep: float = max(0, self.minimal_time_between_tick_iterations - elapsed)
        await asyncio.sleep(sleep)

    def run_simulation_runnables(self):
        self.logger.info("Running simulation runnables...")
        # All simulation should tick based on the begin values of this tick-iteration
        # So, first, all simulations should retrieve their parameters and sensor/command values, then they can tick and publish their values.
        for runnable in self._runnable_sims:
            if runnable.paused:
                continue
            runnable.update_input()

        for runnable in self._runnable_sims:
            if runnable.paused:
                continue

            # Since lockstep requires a synchronized tick with the control,
            # The runnable is ticked successively instead of letting runnable tick itself multiple times at once.
            tick_rate: int = math.ceil(runnable.tick_rate)
            for _ in range(int(tick_rate)):
                runnable.tick()

    def run_control_runnables(self):
        """Control runnables should tick based on the values published by the simulation runnables in this tick-iteration, so they are ticked after the simulation runnables."""
        for runnable in self._runnable_controls:
            tick_rate: int = math.ceil(runnable.tick_rate)
            for _ in range(int(tick_rate)):
                runnable.tick()

    def guard(self, runnables, runner_mode):
        """In lockstep mode, ensure that there are exactly 2 runnables and that one is a simulation and the other is control."""
        from thrs.cli.config.modes import (
            CLIRunnerMode,  # TODO Maapater : Fix circular import
        )

        if runner_mode == CLIRunnerMode.LOCKSTEP:
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
