"""Copy history from old Greptime tables into renamed ones, check it, and drop the old tables.

A spec lists units: one old topic in one old table, copied to one new topic in one new table,
with its columns renamed. Old and new topics never publish side by side, so every row of an
old topic is history of its new topic.

Nothing is kept outside Greptime. Each insert leaves out the timestamps the new topic already
holds, so a run can be stopped and started again, and a second run copies nothing. Two runs
at once would both find a timestamp missing and both insert it, so a run holds a lock: a
table in Greptime that exists while it copies. A drop holds it too, to stay out of a run. The
new tables are append-only: a copied row can't be changed or deleted afterwards, so a unit is
either copied with all its columns or left out and reported.
"""

import logging
import signal
import socket
import time
from collections import defaultdict
from collections.abc import Callable, Generator, Iterable, Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime
from functools import partial
from typing import Any, Self

import psycopg
from pydantic import BaseModel

from zero_data.greptime.config import GreptimeConnection
from zero_data.greptime.migration_spec import MigrationSpec, Unit
from zero_data.greptime.snapshot import open_handle

logger = logging.getLogger(__name__)

SUFFIXES = ("value", "timestamp", "is_valid", "has_value")
DAY_NS = 86_400 * 10**9
COLUMNS_PER_QUERY = 100
LOCK_TABLE = "migrate_history_running"
# Greptime holds an insert in memory: a day of a 1,100-column battery pack in one statement
# took more than 8 GB, an hour of it (4M values) 150 MB.
VALUES_PER_INSERT = 4_000_000
# Greptime's frontend drops its connection to the datanode every few hours of copying
# ("locally-reset streams reached limit"), and the statement in flight fails with an
# internal error or as cancelled.
CONNECTION_DROPPED = (psycopg.errors.InternalError, psycopg.errors.OperatorIntervention)
ATTEMPTS = 5
RETRY_WAIT = 60.0


class MigrationFailed(Exception):
    pass


def quote_ident(name: str) -> str:
    escaped = name.replace('"', '""')
    return f'"{escaped}"'


def quote_literal(value: str) -> str:
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def timestamp_literal(nanos: int) -> str:
    seconds, fraction = divmod(nanos, 10**9)
    return f"'{datetime.fromtimestamp(seconds, UTC):%Y-%m-%dT%H:%M:%S}.{fraction:09d}Z'"


def day_label(nanos: int) -> str:
    return f"{datetime.fromtimestamp(nanos // 10**9, UTC):%Y-%m-%d}"


def day_start(day: date) -> int:
    return int(datetime(day.year, day.month, day.day, tzinfo=UTC).timestamp()) * 10**9


def _chunks(columns: list[str]) -> Iterator[list[str]]:
    for start in range(0, len(columns), COLUMNS_PER_QUERY):
        yield columns[start : start + COLUMNS_PER_QUERY]


class Greptime:
    """Queries against one Greptime database over its Postgres wire endpoint.

    A lost connection is opened again before the next statement. Queries are sent again when
    Greptime drops them or the connection is lost; other statements only through `retried`.
    """

    def __init__(
        self,
        connection: GreptimeConnection,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._connection = connection
        self._dbname = connection.dbname
        self._sleep = sleep
        self._handle = open_handle(connection)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self._handle.close()

    def _open(self) -> psycopg.Connection:
        if self._handle.broken:
            self._handle = open_handle(self._connection)
        return self._handle

    def _fetch(self, sql: str) -> list[tuple[Any, ...]]:
        with self._open().cursor() as cursor:
            cursor.execute(sql)  # pyrefly: ignore[no-matching-overload]
            return cursor.fetchall()

    def retried[T](self, action: Callable[[], T]) -> T:
        """The action's result, trying again when Greptime drops the statement or the
        connection is lost.

        Safe for an insert: it leaves out the timestamps a failed attempt already wrote.
        """
        for attempt in range(1, ATTEMPTS):
            try:
                return action()
            except psycopg.Error as error:
                if not (isinstance(error, CONNECTION_DROPPED) or self._handle.broken):
                    raise
                logger.warning("Attempt %d failed, trying again: %s", attempt, error)
                self._sleep(RETRY_WAIT)
        return action()

    def pause(self, seconds: float) -> None:
        self._sleep(seconds)

    def rows(self, sql: str) -> list[tuple[Any, ...]]:
        return self.retried(partial(self._fetch, sql))

    def run(self, sql: str) -> None:
        with self._open().cursor() as cursor:
            cursor.execute(sql)  # pyrefly: ignore[no-matching-overload]

    def count(self, sql: str) -> int:
        ((found,),) = self.rows(sql)
        return int(found)

    def tables(self) -> set[str]:
        found = self.rows(
            "SELECT table_name FROM information_schema.tables "
            f"WHERE table_schema = {quote_literal(self._dbname)}"
        )
        return {name for (name,) in found}

    def columns(self, table: str) -> dict[str, str]:
        found = self.rows(
            "SELECT column_name, data_type FROM information_schema.columns "
            f"WHERE table_schema = {quote_literal(self._dbname)} "
            f"AND table_name = {quote_literal(table)}"
        )
        return {name: data_type for name, data_type in found}


def _rows_with_a_value(old_topic: str, pairs: list[tuple[str, str]]) -> str:
    values = [old for old, _ in pairs if old.endswith("__value")]
    has_value = " OR ".join(f"{quote_ident(c)} IS NOT NULL" for c in values)
    return f"{quote_ident('topic')} = {quote_literal(old_topic)} AND ({has_value})"


class Copy(BaseModel):
    """A unit with the columns it copies, as found in the old table."""

    unit: Unit
    pairs: list[tuple[str, str]]
    constants: dict[str, str]
    days: dict[int, int]
    last: int

    @property
    def rows(self) -> int:
        return sum(self.days.values())

    def old_rows(self) -> str:
        return _rows_with_a_value(self.unit.old_topic, self.pairs)

    def slices(self, day: int) -> list[tuple[int, int]]:
        """The day in equal parts, each small enough for one insert."""
        parts = -(-self.days[day] * len(self.pairs) // VALUES_PER_INSERT)
        edges = [day + DAY_NS * part // parts for part in range(parts + 1)]
        return list(zip(edges, edges[1:], strict=False))

    def insert_sql(self, start: int, end: int) -> str:
        in_day = (
            f'"timestamp" >= {timestamp_literal(start)} '
            f'AND "timestamp" < {timestamp_literal(end)}'
        )
        targets = [
            '"timestamp"',
            *(quote_ident(column) for column in self.constants),
            *(quote_ident(new) for _, new in self.pairs),
        ]
        sources = [
            '"timestamp"',
            *(quote_literal(value) for value in self.constants.values()),
            *(quote_ident(old) for old, _ in self.pairs),
        ]
        copied_before = " OR ".join(
            f"{quote_ident(new)} IS NOT NULL"
            for _, new in self.pairs
            if new.endswith("__value")
        )
        return (
            f"INSERT INTO {quote_ident(self.unit.new_table)} ({', '.join(targets)})\n"
            f"SELECT {', '.join(sources)}\n"
            f"FROM {quote_ident(self.unit.old_table)}\n"
            f"WHERE {self.old_rows()} AND {in_day}\n"
            f'AND "timestamp" NOT IN (SELECT "timestamp" '
            f"FROM {quote_ident(self.unit.new_table)} "
            f"WHERE {quote_ident('topic')} = {quote_literal(self.unit.new_topic)} "
            f"AND {in_day} AND ({copied_before}))"
        )


class Mismatch(BaseModel):
    old_table: str
    old_column: str
    old_type: str
    new_table: str
    new_column: str
    new_type: str


class Refusal(BaseModel):
    unit: Unit
    reason: str


class History(BaseModel):
    """Everything that goes to one new topic: usually one unit, more for earlier names."""

    new_table: str
    new_topic: str
    copies: list[Copy]
    present: dict[int, int]

    @property
    def expected(self) -> dict[int, int]:
        days: dict[int, int] = defaultdict(int)
        for copy in self.copies:
            for day, rows in copy.days.items():
                days[day] += rows
        return dict(days)

    @property
    def last(self) -> int:
        return max(copy.last for copy in self.copies)

    def new_rows(self) -> str:
        return (
            f"{quote_ident('topic')} = {quote_literal(self.new_topic)} "
            f'AND "timestamp" <= {timestamp_literal(self.last)}'
        )


class Leftover(BaseModel):
    """What an old table holds that no unit copies."""

    topics: dict[str, int]
    columns: dict[str, list[str]]

    def __bool__(self) -> bool:
        return bool(self.topics or self.columns)


class Migration(BaseModel):
    histories: list[History]
    additions: dict[str, dict[str, str]]
    mismatches: list[Mismatch]
    refused: list[Refusal]

    def touching(self, old_table: str) -> list[History]:
        return [
            history
            for history in self.histories
            if any(copy.unit.old_table == old_table for copy in history.copies)
        ]


def _days(greptime: Greptime, table: str, where: str) -> list[tuple[int, int, int]]:
    found = greptime.rows(
        "SELECT CAST(date_trunc('day', \"timestamp\") AS BIGINT), count(*), "
        f'CAST(max("timestamp") AS BIGINT) FROM {quote_ident(table)} '
        f"WHERE {where} GROUP BY 1"
    )
    return [(int(day), int(rows), int(last)) for day, rows, last in found]


def load(
    greptime: Greptime,
    spec: MigrationSpec,
    old_tables: Iterable[str] = (),
    up_to: date | None = None,
) -> Migration:
    """Read what there is to copy and what is already there, up to and including a day. Only reads."""
    before_next_day = (
        f' AND "timestamp" < {timestamp_literal(day_start(up_to) + DAY_NS)}'
        if up_to
        else ""
    )
    selected = set(old_tables)
    unknown = sorted(selected - set(spec.old_tables))
    if unknown:
        raise MigrationFailed(f"Not an old table of the spec: {unknown}")
    wanted_topics = {
        (unit.new_table, unit.new_topic)
        for unit in spec.units
        if not selected or unit.old_table in selected
    }
    units = [u for u in spec.units if (u.new_table, u.new_topic) in wanted_topics]
    present_tables = greptime.tables()
    schemas = {
        table: greptime.columns(table)
        for table in sorted({u.old_table for u in units} | {u.new_table for u in units})
        if table in present_tables
    }

    additions: dict[str, dict[str, str]] = defaultdict(dict)
    mismatches: list[Mismatch] = []
    refused: list[Refusal] = []
    copies: dict[tuple[str, str], list[Copy]] = defaultdict(list)
    for unit in units:
        if unit.old_table not in schemas:
            refused.append(Refusal(unit=unit, reason="The old table doesn't exist"))
            continue
        if unit.new_table not in schemas:
            refused.append(Refusal(unit=unit, reason="The new table doesn't exist"))
            continue
        old_schema, new_schema = schemas[unit.old_table], schemas[unit.new_table]
        missing = sorted({"topic", "technical_name"} - set(new_schema))
        if missing:
            refused.append(
                Refusal(unit=unit, reason=f"The new table has no {missing} column")
            )
            continue
        pairs = [
            (f"{column.old}__{suffix}", f"{column.new}__{suffix}")
            for column in unit.columns
            for suffix in SUFFIXES
            if f"{column.old}__{suffix}" in old_schema
        ]
        if not any(old.endswith("__value") for old, _ in pairs):
            continue
        source_type = (
            [("source_type", "source_type")]
            if "source_type" in old_schema and "source_type" in new_schema
            else []
        )
        known = {**new_schema, **additions[unit.new_table]}
        unit_mismatches = [
            Mismatch(
                old_table=unit.old_table,
                old_column=old,
                old_type=old_schema[old],
                new_table=unit.new_table,
                new_column=new,
                new_type=known[new],
            )
            for old, new in pairs
            if new in known and known[new] != old_schema[old]
        ]
        if unit_mismatches:
            mismatches.extend(unit_mismatches)
            refused.append(
                Refusal(
                    unit=unit,
                    reason=f"{len(unit_mismatches)} columns differ in type",
                )
            )
            continue
        copy_days = _days(
            greptime,
            unit.old_table,
            _rows_with_a_value(unit.old_topic, pairs) + before_next_day,
        )
        if not copy_days:
            continue
        additions[unit.new_table].update(
            {new: old_schema[old] for old, new in pairs if new not in known}
        )
        copies[(unit.new_table, unit.new_topic)].append(
            Copy(
                unit=unit,
                pairs=[*pairs, *source_type],
                constants={
                    "topic": unit.new_topic,
                    "technical_name": unit.technical_name,
                    **({"table": unit.new_table} if "table" in new_schema else {}),
                },
                days={day: rows for day, rows, _ in copy_days},
                last=max(last for _, _, last in copy_days),
            )
        )

    histories = []
    for (new_table, new_topic), topic_copies in sorted(copies.items()):
        history = History(
            new_table=new_table, new_topic=new_topic, copies=topic_copies, present={}
        )
        present = {
            day: rows
            for day, rows, _ in _days(
                greptime, new_table, history.new_rows() + before_next_day
            )
        }
        expected = history.expected
        surplus = sorted(
            day for day, rows in present.items() if rows > expected.get(day, 0)
        )
        if surplus:
            refused.extend(
                Refusal(
                    unit=copy.unit,
                    reason="The new topic holds more rows than the old topics have: "
                    + ", ".join(
                        f"{present[day]} against {expected.get(day, 0)} on "
                        f"{day_label(day)}"
                        for day in surplus[:5]
                    ),
                )
                for copy in topic_copies
            )
            continue
        histories.append(history.model_copy(update={"present": present}))
    return Migration(
        histories=histories,
        additions={
            table: dict(sorted(columns.items()))
            for table, columns in sorted(additions.items())
            if columns
        },
        mismatches=mismatches,
        refused=refused,
    )


def leftover(greptime: Greptime, spec: MigrationSpec, old_table: str) -> Leftover:
    """The topics and columns with data in an old table that no unit copies."""
    copied: dict[str, set[str]] = defaultdict(set)
    for unit in spec.units:
        if unit.old_table == old_table:
            copied[unit.old_topic].update(f"{c.old}__value" for c in unit.columns)
    value_columns = sorted(
        column for column in greptime.columns(old_table) if column.endswith("__value")
    )
    topics: dict[str, int] = {}
    columns: dict[str, set[str]] = defaultdict(set)
    for chunk in _chunks(value_columns) if value_columns else [[]]:
        counts = ", ".join(f"count({quote_ident(column)})" for column in chunk)
        found = greptime.rows(
            f"SELECT {quote_ident('topic')}, count(*){', ' if chunk else ''}{counts} "
            f"FROM {quote_ident(old_table)} GROUP BY 1"
        )
        for topic, rows, *filled in found:
            if topic not in copied:
                topics[topic] = int(rows)
                continue
            columns[topic].update(
                column
                for column, count in zip(chunk, filled, strict=True)
                if count and column not in copied[topic]
            )
    return Leftover(
        topics=dict(sorted(topics.items())),
        columns={
            topic: sorted(found) for topic, found in sorted(columns.items()) if found
        },
    )


def _table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    body = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    if not body:
        return "None."
    rule = "|" + "|".join("---" for _ in headers) + "|"
    return "\n".join(["| " + " | ".join(headers) + " |", rule, *body])


def report(migration: Migration, leftovers: dict[str, Leftover]) -> str:
    """What a run would do, as markdown."""
    per_table: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    for history in migration.histories:
        present = sum(history.present.values())
        for index, copy in enumerate(history.copies):
            totals = per_table[copy.unit.old_table]
            totals[0] += 1
            totals[1] += copy.rows
            totals[2] += present if index == 0 else 0
    to_copy = sum(rows for _, rows, _ in per_table.values())
    there = sum(present for _, _, present in per_table.values())
    sections = [
        f"# History migration: {to_copy:,} rows in "
        f"{sum(units for units, _, _ in per_table.values())} units, "
        f"{there:,} already copied",
        "## Per old table",
        _table(
            ["Old table", "Units", "Rows", "Already in the new tables"],
            (
                (f"`{table}`", units, f"{rows:,}", f"{present:,}")
                for table, (units, rows, present) in sorted(per_table.items())
            ),
        ),
        f"## Units left out ({len(migration.refused)})",
        "A unit is copied with all its columns or not at all. Fix the cause and run "
        "again.",
        _table(
            ["Old table", "Old topic", "New topic", "Reason"],
            (
                (
                    f"`{r.unit.old_table}`",
                    f"`{r.unit.old_topic}`",
                    f"`{r.unit.new_topic}`",
                    r.reason,
                )
                for r in migration.refused
            ),
        ),
        f"## Columns that differ in type ({len(migration.mismatches)})",
        "Decide per column which side is wrong and alter that one before the run: "
        '`ALTER TABLE "<table>" MODIFY COLUMN "<column>" <TYPE>`.',
        _table(
            ["Old table", "Old column", "Type", "New table", "New column", "Type"],
            (
                (
                    f"`{m.old_table}`",
                    f"`{m.old_column}`",
                    m.old_type,
                    f"`{m.new_table}`",
                    f"`{m.new_column}`",
                    m.new_type,
                )
                for m in migration.mismatches
            ),
        ),
        "## Columns the run adds",
        "A new table gets a column when its first value arrives. These have none yet, "
        "so the run adds them with the old column's type.",
        _table(
            ["New table", "Columns"],
            (
                (f"`{table}`", len(columns))
                for table, columns in migration.additions.items()
            ),
        ),
        "## Not migrated",
        "Data in the old tables that no unit copies. It is lost when the table is "
        "dropped.",
        _table(
            ["Old table", "Topic", "Rows", "Columns with values"],
            (
                row
                for table, left in sorted(leftovers.items())
                for row in [
                    *(
                        (f"`{table}`", f"`{topic}`", f"{rows:,}", "all")
                        for topic, rows in left.topics.items()
                    ),
                    *(
                        (
                            f"`{table}`",
                            f"`{topic}`",
                            "",
                            ", ".join(f"`{c}`" for c in columns),
                        )
                        for topic, columns in left.columns.items()
                    ),
                ]
            ),
        ),
    ]
    return "\n\n".join(sections) + "\n"


@contextmanager
def lock(greptime: Greptime, unlock: bool = False) -> Generator[None]:
    """Hold the lock that keeps runs and drops apart; `unlock` first clears one left behind.

    A run that loses its connection can't release the lock, and its last insert may still be
    going on in Greptime. Give the lock a connection of its own: Ctrl-C cancels the statement
    on the connection that copies, and reaches the process more than once under `uv run`.
    """
    if unlock:
        greptime.run(f"DROP TABLE IF EXISTS {quote_ident(LOCK_TABLE)}")
    try:
        greptime.run(
            f"CREATE TABLE {quote_ident(LOCK_TABLE)} "
            '("started" TIMESTAMP(3) TIME INDEX, "host" STRING)'
        )
    except psycopg.Error as error:
        if LOCK_TABLE not in greptime.tables():
            raise
        holders = ", ".join(
            f"{host} since {started}"
            for started, host in greptime.rows(
                f'SELECT "started", "host" FROM {quote_ident(LOCK_TABLE)}'
            )
        )
        raise MigrationFailed(
            f"A run or drop holds the lock ({holders or 'just started'}). If it has "
            "ended, wait a minute for its last insert and start again with --unlock."
        ) from error
    greptime.run(
        f"INSERT INTO {quote_ident(LOCK_TABLE)} VALUES "
        f"(now(), {quote_literal(socket.gethostname())})"
    )
    try:
        yield
    finally:
        interrupt = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            greptime.run(f"DROP TABLE {quote_ident(LOCK_TABLE)}")
        except psycopg.Error:
            logger.warning(
                "Could not release the lock; the next run or drop needs --unlock"
            )
        finally:
            signal.signal(signal.SIGINT, interrupt)


def run(
    greptime: Greptime,
    migration: Migration,
    until: date | None = None,
    pause: float = 0.1,
) -> int:
    """Copy day by day, newest first, across all units; returns the rows copied."""
    for table, columns in migration.additions.items():
        for column, column_type in columns.items():
            greptime.run(
                f"ALTER TABLE {quote_ident(table)} ADD COLUMN "
                f"{quote_ident(column)} {column_type.upper()} NULL"
            )
    oldest = day_start(until) if until else 0
    days = sorted(
        {day for h in migration.histories for day in h.expected if day >= oldest},
        reverse=True,
    )
    copied = 0
    for day in days:
        copied_today = 0
        for history in migration.histories:
            expected = history.expected.get(day, 0)
            present = history.present.get(day, 0)
            if present == expected:
                continue
            for copy in history.copies:
                if day in copy.days:
                    for start, end in copy.slices(day):
                        greptime.retried(
                            partial(greptime.run, copy.insert_sql(start, end))
                        )
            rows_of_the_day = (
                f"SELECT count(*) FROM {quote_ident(history.new_table)} "
                f"WHERE {history.new_rows()} "
                f'AND "timestamp" >= {timestamp_literal(day)} '
                f'AND "timestamp" < {timestamp_literal(day + DAY_NS)}'
            )
            there = greptime.count(rows_of_the_day)
            if there != expected:
                raise MigrationFailed(
                    f"{history.new_topic} holds {there} rows on {day_label(day)} "
                    f"after copying, {expected} expected"
                )
            copied_today += there - present
            greptime.pause(pause)
        copied += copied_today
        logger.info("%s: %d rows copied", day_label(day), copied_today)
    return copied


def _aggregates(
    greptime: Greptime, table: str, where: str, columns: list[str]
) -> dict[str, tuple[Any, ...]]:
    found: dict[str, tuple[Any, ...]] = {}
    for chunk in _chunks(columns):
        selected = ", ".join(
            f"count({quote_ident(c)}), min({quote_ident(c)}), max({quote_ident(c)})"
            for c in chunk
        )
        (values,) = greptime.rows(
            f"SELECT {selected} FROM {quote_ident(table)} WHERE {where}"
        )
        found.update(
            {
                column: tuple(values[3 * index : 3 * index + 3])
                for index, column in enumerate(chunk)
            }
        )
    return found


def _merged(stats: list[tuple[Any, ...]]) -> tuple[Any, ...]:
    lows = [low for _, low, _ in stats if low is not None]
    highs = [high for _, _, high in stats if high is not None]
    return (
        sum(count for count, _, _ in stats),
        min(lows) if lows else None,
        max(highs) if highs else None,
    )


def check(greptime: Greptime, migration: Migration) -> list[str]:
    """Where the new tables differ from the old ones; empty when the copy is complete.

    Per new topic it compares the rows per day, and `count`, `min` and `max` of every copied
    column, between the old topics and the new topic up to the old topics' last row.
    """
    findings = [
        f"{r.unit.old_table} {r.unit.label}: left out. {r.reason}"
        for r in migration.refused
    ]
    for history in migration.histories:
        expected = history.expected
        findings.extend(
            f"{history.new_table} {history.new_topic} {day_label(day)}: "
            f"{expected.get(day, 0)} old rows, {history.present.get(day, 0)} new rows"
            for day in sorted(set(expected) | set(history.present))
            if expected.get(day, 0) != history.present.get(day, 0)
        )
        old_stats: dict[str, list[tuple[Any, ...]]] = defaultdict(list)
        for copy in history.copies:
            stats = _aggregates(
                greptime,
                copy.unit.old_table,
                copy.old_rows(),
                [old for old, _ in copy.pairs],
            )
            for old, new in copy.pairs:
                old_stats[new].append(stats[old])
        new_schema = greptime.columns(history.new_table)
        absent: dict[str, tuple[Any, ...]] = {
            column: (0, None, None) for column in old_stats if column not in new_schema
        }
        new_stats = absent | _aggregates(
            greptime,
            history.new_table,
            history.new_rows(),
            sorted(set(old_stats) - set(absent)),
        )
        findings.extend(
            f"{history.new_table} {history.new_topic} {column}: count, min, max "
            f"{_merged(old_stats[column])} old, {new_stats[column]} new"
            for column in sorted(old_stats)
            if _merged(old_stats[column]) != new_stats[column]
        )
    return findings


def drop(
    greptime: Greptime,
    spec: MigrationSpec,
    old_tables: list[str],
    accept_unmigrated: bool,
    execute: bool,
) -> dict[str, str]:
    """Drop the old tables whose history is in the new ones; returns what happened per table.

    Without tables it takes every old table of the spec. A table is kept while a check finds a
    difference, while it still receives rows, or while it holds data no unit copies. That
    last one is overridden by naming the table with `accept_unmigrated`.

    Every table is checked before any is dropped: old tables that feed the same new topic can
    only be checked while all of them exist.
    """
    migration = load(greptime, spec, old_tables)
    present_tables = greptime.tables()
    outcomes: dict[str, str] = {}
    for table in old_tables or spec.old_tables:
        if table not in present_tables:
            outcomes[table] = "already gone"
            continue
        selected = Migration(
            histories=migration.touching(table),
            additions={},
            mismatches=[],
            refused=[r for r in migration.refused if r.unit.old_table == table],
        )
        findings = check(greptime, selected)
        recent = greptime.count(
            f"SELECT count(*) FROM {quote_ident(table)} "
            "WHERE \"timestamp\" > now() - INTERVAL '1 day'"
        )
        left = leftover(greptime, spec, table)
        reasons = [
            *([f"{len(findings)} check findings"] if findings else []),
            *([f"{recent} rows in the last day"] if recent else []),
            *(
                [
                    f"not migrated: {len(left.topics)} topics, and columns of "
                    f"{len(left.columns)} migrated topics"
                ]
                if left and not (accept_unmigrated and table in old_tables)
                else []
            ),
        ]
        outcomes[table] = (
            "kept: " + "; ".join(reasons) if reasons else "would be dropped"
        )
    if not execute:
        return outcomes
    for table, outcome in outcomes.items():
        if outcome == "would be dropped":
            greptime.run(f"DROP TABLE {quote_ident(table)}")
    return {
        table: "dropped" if outcome == "would be dropped" else outcome
        for table, outcome in outcomes.items()
    }
