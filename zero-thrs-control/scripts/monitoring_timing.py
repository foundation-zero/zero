"""Time the monitoring history queries the DHW page makes, against a real GreptimeDB.

uv run python scripts/monitoring_timing.py --greptime_url mysql://app@greptime-zero.tail0b4840.ts.net:4002/public
"""
# ruff: noqa: INP001 - a standalone script, not part of a package

import asyncio
import time
from datetime import UTC, datetime, timedelta

from pydantic_settings import BaseSettings, CliApp

from thrs.monitoring.history import MonitoringHistory, create_engine
from thrs.monitoring.segments import merge_segments
from thrs.monitoring.sources import (
    MonitoringMetric,
    MonitoringModule,
    MonitoringSignal,
    state_source,
)

MODULE = MonitoringModule.DHW
RANGES = (timedelta(hours=6), timedelta(hours=24), timedelta(days=7))

# One entry per page section, as each section is one request.
SECTIONS: dict[str, list[MonitoringMetric]] = {
    "tank temperatures": [
        MonitoringMetric.TEMPERATURE,
        MonitoringMetric.MINIMUM_TANK_TEMPERATURE,
        MonitoringMetric.MAXIMUM_TANK_TEMPERATURE,
    ],
    "tank levels": [
        MonitoringMetric.LEVEL,
        MonitoringMetric.MINIMUM_TANK_LEVEL,
        MonitoringMetric.MAXIMUM_TANK_LEVEL,
    ],
    "pumps": [MonitoringMetric.PUMP_SPEED],
    "valves": [MonitoringMetric.VALVE_POSITION_ABSOLUTE],
    "flow": [MonitoringMetric.FLOW],
    "temperatures": [MonitoringMetric.TEMPERATURE],
    "pressure": [MonitoringMetric.PRESSURE],
}
STATE_SECTIONS = [
    [MonitoringSignal.BOOSTING_MODE, MonitoringSignal.FILLING_MODE],
    [
        MonitoringSignal.TANK_1_STATE,
        MonitoringSignal.TANK_2_STATE,
        MonitoringSignal.TANK_3_STATE,
    ],
]
TANK_TEMPERATURES = [
    "dhw-temperature-tank1",
    "dhw-temperature-tank2",
    "dhw-temperature-tank3",
]


async def _time_series(
    history: MonitoringHistory,
    name: str,
    metrics: list[MonitoringMetric],
    start: datetime,
    end: datetime,
) -> str:
    began = time.perf_counter()
    devices = TANK_TEMPERATURES if name == "tank temperatures" else None
    async with asyncio.TaskGroup() as group:
        tasks = [
            group.create_task(history.series(MODULE, metric, start, end, devices))
            for metric in metrics
        ]
    points = sum(
        len(device.times) for task in tasks for device in task.result().devices
    )
    return f"{name}: {time.perf_counter() - began:.2f} s, {points} points"


async def _time_states(
    history: MonitoringHistory,
    signals: list[MonitoringSignal],
    start: datetime,
    end: datetime,
) -> str:
    began = time.perf_counter()
    async with asyncio.TaskGroup() as group:
        tasks = [
            group.create_task(history.states(MODULE, signal, start, end))
            for signal in signals
        ]
    segments = sum(
        len(
            merge_segments(
                task.result(), start, end, state_source(MODULE, signal).null_state
            )
        )
        for signal, task in zip(signals, tasks, strict=True)
    )
    return f"states {', '.join(signals)}: {time.perf_counter() - began:.2f} s, {segments} segments"


async def _time_page(history: MonitoringHistory, span: timedelta) -> list[str]:
    end = datetime.now(UTC)
    start = end - span
    began = time.perf_counter()
    async with asyncio.TaskGroup() as group:
        tasks = [
            *(
                group.create_task(_time_states(history, signals, start, end))
                for signals in STATE_SECTIONS
            ),
            *(
                group.create_task(_time_series(history, name, metrics, start, end))
                for name, metrics in SECTIONS.items()
            ),
        ]
    return [
        f"== {span}: whole page {time.perf_counter() - began:.2f} s",
        *(f"  {task.result()}" for task in tasks),
    ]


class Timing(BaseSettings):
    greptime_url: str

    async def cli_cmd(self) -> None:
        engine = create_engine(self.greptime_url)
        history = MonitoringHistory(engine)
        try:
            for span in RANGES:
                print("\n".join(await _time_page(history, span)))  # noqa: T201
        finally:
            await engine.dispose()


if __name__ == "__main__":
    CliApp.run(Timing)
