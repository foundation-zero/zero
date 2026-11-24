import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from itertools import groupby
from typing import Any

from pydantic import BaseModel
from sqlalchemy import Row, TextClause, bindparam, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from thrs.monitoring.bins import bin_size
from thrs.monitoring.segments import STALE_AFTER, Sample
from thrs.monitoring.sources import (
    SERIES_SOURCES,
    MonitoringMetric,
    MonitoringModule,
    MonitoringSignal,
    ParameterSource,
    SensorSource,
    state_source,
)

QUERY_TIMEOUT = timedelta(seconds=20)

# How far before the range to look for the state or parameter value it opens with.
OPENING_LOOKBACK = timedelta(days=1)
PARAMETER_LOOKBACK = timedelta(days=30)


class Reading(BaseModel, frozen=True):
    value: float
    timestamp: datetime


class DeviceSeries(BaseModel, frozen=True):
    device: str
    yard_tag: str | None
    times: list[datetime]
    values: list[float]
    latest: Reading | None


class MetricSeries(BaseModel, frozen=True):
    metric: MonitoringMetric
    unit: str | None
    step: bool
    bin: timedelta | None
    devices: list[DeviceSeries]


def create_engine(greptime_url: str) -> AsyncEngine:
    """An engine for GreptimeDB's MySQL protocol, e.g. mysql://app@greptimedb:4002/public.

    Creating it does not connect, so an unreachable GreptimeDB only fails the
    monitoring queries, not the start of the API.
    """
    return create_async_engine(
        greptime_url.replace("mysql://", "mysql+aiomysql://", 1),
        pool_pre_ping=True,
        # Idle connections over a VPN can be dropped silently; replace them early
        # rather than stall on one.
        pool_recycle=60,
        # A page load runs about 30 queries at once, two per metric or signal;
        # keeping that many open saves a reconnect per query on every refresh.
        pool_size=30,
        max_overflow=30,
        connect_args={"connect_timeout": 5},
    )


def _utc(timestamp: datetime) -> datetime:
    return timestamp.replace(tzinfo=UTC)


def _change_points_sql(table: str, column: str, technical_name: str | None) -> str:
    name_filter = "AND technical_name = :technical_name" if technical_name else ""
    return f"""
        SELECT timestamp, value FROM (
            SELECT timestamp, {column} AS value,
                LAG({column}) OVER (ORDER BY timestamp) AS previous,
                LAG(timestamp) OVER (ORDER BY timestamp) AS previous_timestamp,
                LEAD(timestamp) OVER (ORDER BY timestamp) AS next_timestamp
            FROM {table}
            WHERE timestamp >= :start AND timestamp < :end {name_filter}
        )
        WHERE previous_timestamp IS NULL OR next_timestamp IS NULL
            OR previous IS DISTINCT FROM value
        ORDER BY timestamp
    """  # noqa: S608 - table and column come from the source registry, never from the client


def _opening_sql(table: str, column: str, technical_name: str | None) -> str:
    name_filter = "AND technical_name = :technical_name" if technical_name else ""
    return f"""
        SELECT timestamp, {column} AS value FROM {table}
        WHERE timestamp < :start AND timestamp >= :lookback {name_filter}
        ORDER BY timestamp DESC LIMIT 1
    """  # noqa: S608 - table and column come from the source registry, never from the client


class MonitoringHistory:
    """Reads THRS history from GreptimeDB for the monitoring page."""

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def series(
        self,
        module: MonitoringModule,
        metric: MonitoringMetric,
        start: datetime,
        end: datetime,
        devices: Sequence[str] | None = None,
        bin_width: timedelta | None = None,
    ) -> MetricSeries:
        match SERIES_SOURCES[metric]:
            case SensorSource() as source:
                return await self._sensor_series(
                    module, metric, source, start, end, devices, bin_width
                )
            case ParameterSource() as source:
                return await self._parameter_series(module, metric, source, start, end)

    async def states(
        self,
        module: MonitoringModule,
        signal: MonitoringSignal,
        start: datetime,
        end: datetime,
    ) -> list[Sample]:
        source = state_source(module, signal)
        rows = await self._change_points(
            source.table, source.column, start, end, source.technical_name
        )
        return [
            Sample(timestamp=timestamp, state=source.state(value))
            for timestamp, value in rows
        ]

    async def _sensor_series(
        self,
        module: MonitoringModule,
        metric: MonitoringMetric,
        source: SensorSource,
        start: datetime,
        end: datetime,
        devices: Sequence[str] | None,
        bin_width: timedelta | None = None,
    ) -> MetricSeries:
        size = bin_width or bin_size(start, end)
        expression = (
            f"CAST({source.column} AS INT)" if source.as_integer else source.column
        )
        if source.scale is not None:
            expression = f"{expression} * {source.scale!r}"
        yard_tag = "yard_tag" if source.has_yard_tag else "NULL"
        device_filter = "AND technical_name IN :devices" if devices else ""
        where = f"""
            FROM {source.table}
            WHERE timestamp >= :start AND timestamp < :end
                AND topic LIKE :topic_prefix {device_filter}
        """
        binned = text(f"""
            SELECT date_bin(INTERVAL {int(size.total_seconds())} second, timestamp) AS bin,
                technical_name, {yard_tag} AS yard_tag,
                {source.aggregate}({expression}) AS value
            {where}
            GROUP BY bin, technical_name{", yard_tag" if source.has_yard_tag else ""}
            ORDER BY technical_name, bin
        """)
        latest = text(f"""
            SELECT technical_name, last_value({expression} ORDER BY timestamp) AS value,
                max(timestamp) AS timestamp
            {where}
            GROUP BY technical_name
        """)
        parameters: dict[str, Any] = {
            "start": start,
            "end": end,
            "topic_prefix": source.topic_prefix(module),
        }
        if devices:
            parameters["devices"] = list(devices)
            binned = binned.bindparams(bindparam("devices", expanding=True))
            latest = latest.bindparams(bindparam("devices", expanding=True))

        async with asyncio.TaskGroup() as group:
            binned_task = group.create_task(self._fetch(binned, parameters))
            latest_task = group.create_task(self._fetch(latest, parameters))

        readings = {
            name: Reading(value=float(value), timestamp=_utc(timestamp))
            for name, value, timestamp in latest_task.result()
            if value is not None
        }
        device_series = [
            DeviceSeries(
                device=name,
                yard_tag=rows[0].yard_tag or None,
                times=[_utc(row.bin) for row in rows],
                values=[float(row.value) for row in rows],
                latest=readings.get(name),
            )
            for name, group_rows in groupby(
                (row for row in binned_task.result() if row.value is not None),
                key=lambda row: row.technical_name,
            )
            if (rows := list(group_rows))
        ]
        return MetricSeries(
            metric=metric, unit=source.unit, step=False, bin=size, devices=device_series
        )

    async def _parameter_series(
        self,
        module: MonitoringModule,
        metric: MonitoringMetric,
        source: ParameterSource,
        start: datetime,
        end: datetime,
    ) -> MetricSeries:
        rows = [
            (max(timestamp, start), float(value))
            # Parameters are set rarely, so look back further for the value the
            # range opens with; without it the limits would start at the first set.
            for timestamp, value in await self._change_points(
                source.table(module),
                source.column,
                start,
                end,
                lookback=PARAMETER_LOOKBACK,
            )
            if value is not None
        ]
        if not rows:
            return MetricSeries(
                metric=metric, unit=source.unit, step=True, bin=None, devices=[]
            )

        last_timestamp, last_value = rows[-1]
        close = end if end - last_timestamp <= STALE_AFTER else last_timestamp
        # The first and last samples come back even when unchanged; a step only
        # needs the points where the value changes.
        changes = [
            row
            for previous, row in zip([None, *rows], rows, strict=False)
            if previous is None or previous[1] != row[1]
        ]
        points = [*changes, (close, last_value)]
        return MetricSeries(
            metric=metric,
            unit=source.unit,
            step=True,
            bin=None,
            devices=[
                DeviceSeries(
                    device=source.column,
                    yard_tag=None,
                    times=[timestamp for timestamp, _ in points],
                    values=[value for _, value in points],
                    latest=Reading(value=last_value, timestamp=last_timestamp),
                )
            ],
        )

    async def alarm_changes(
        self, module: MonitoringModule, start: datetime, end: datetime
    ) -> list[tuple[datetime, Any]]:
        """The module alarm at its change points, opening with its value at `start`."""
        return await self._change_points(
            f"marpower__500000_thrs__{module}__alarm", "alarm__value", start, end
        )

    async def parameter_sets(
        self, module: MonitoringModule, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        """The parameter sets sent to the module in the range, after the last one before it."""
        table = f"thrs__controller__{module}__parameters__set"
        # Sets are rare, so look back further for the one the range opens with.
        parameters = {
            "start": start,
            "end": end,
            "lookback": start - PARAMETER_LOOKBACK,
        }
        async with asyncio.TaskGroup() as group:
            opening = group.create_task(
                self._fetch(
                    text(f"""
                        SELECT * FROM {table}
                        WHERE timestamp < :start AND timestamp >= :lookback
                        ORDER BY timestamp DESC LIMIT 1
                    """),  # noqa: S608 - the table name comes from the module enum
                    parameters,
                )
            )
            in_range = group.create_task(
                self._fetch(
                    text(f"""
                        SELECT * FROM {table}
                        WHERE timestamp >= :start AND timestamp < :end
                        ORDER BY timestamp
                    """),  # noqa: S608 - the table name comes from the module enum
                    parameters,
                )
            )
        return [dict(row._mapping) for row in [*opening.result(), *in_range.result()]]

    async def _change_points(
        self,
        table: str,
        column: str,
        start: datetime,
        end: datetime,
        technical_name: str | None = None,
        lookback: timedelta = OPENING_LOOKBACK,
    ) -> list[tuple[datetime, Any]]:
        """The opening value before `start`, every change in the range and the last sample."""
        parameters = {
            "start": start,
            "end": end,
            "lookback": start - lookback,
            "technical_name": technical_name,
        }
        async with asyncio.TaskGroup() as group:
            opening_task = group.create_task(
                self._fetch(
                    text(_opening_sql(table, column, technical_name)), parameters
                )
            )
            changes_task = group.create_task(
                self._fetch(
                    text(_change_points_sql(table, column, technical_name)),
                    parameters,
                )
            )
        return [
            (_utc(timestamp), value)
            for timestamp, value in [*opening_task.result(), *changes_task.result()]
        ]

    async def _fetch(
        self, statement: TextClause, parameters: dict[str, Any]
    ) -> Sequence[Row[*tuple[Any, ...]]]:
        async with (
            asyncio.timeout(QUERY_TIMEOUT.total_seconds()),
            self._engine.connect() as connection,
        ):
            return (await connection.execute(statement, parameters)).all()
