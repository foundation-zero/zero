"""Copy history from old Greptime tables into new ones, through a reviewed SQL file.

`plan` only reads. Per wave of the spec it writes the SQL to run (`wave-<n>.sql`), a manifest
(`wave-<n>.plan.json`) and a dry-run report (`wave-<n>.report.md`). The same spec and the same
Greptime state give byte-identical files.

`execute` runs a planned SQL file as it is, one statement at a time, and appends each to
`wave-<n>.journal.jsonl`. A restart skips what the journal shows as done, and a window whose
rows are already all in the new table.

`check` compares, per unit, the old rows with a mapped value against the new rows, day by day,
and `count`, `min` and `max` of a sample of columns, and writes `wave-<n>.check.md`.

Rows are copied only before a unit's bound: the new topic's first row in the new table at plan
time, or the cut-over boundary for a topic that has none. The bounds are read once, by `plan`;
after a copy the new topic's first row is the copied history, so `execute` and `check` read
the bounds from the manifest.
"""

import hashlib
import json
import logging
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import psycopg
from pydantic import BaseModel

from zero_data.greptime.migration_spec import SUFFIXES, MigrationSpec, Unit

logger = logging.getLogger(__name__)

DAY_NS = 86_400 * 10**9
SAMPLED_COLUMNS = 3

# Casts that keep every value. Anything else (string to number, double to bigint) stops the unit.
LOSSLESS_CASTS = {
    ("boolean", "bigint"),
    ("boolean", "double"),
    ("boolean", "string"),
    ("bigint", "double"),
    ("bigint", "string"),
    ("double", "string"),
}


class MigrationRefused(Exception):
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


def to_nanos(moment: datetime) -> int:
    return int(moment.timestamp()) * 10**9 + moment.microsecond * 1000


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class Greptime:
    """Queries against one Greptime database over its Postgres wire endpoint."""

    def __init__(self, handle: psycopg.Connection, dbname: str) -> None:
        self._handle = handle
        self._dbname = dbname

    def rows(self, sql: str) -> list[tuple[Any, ...]]:
        with self._handle.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def run(self, sql: str) -> None:
        with self._handle.cursor() as cursor:
            cursor.execute(sql)

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


class ColumnCopy(BaseModel):
    old: str
    new: str
    type: str
    cast: bool

    @property
    def expression(self) -> str:
        if self.cast:
            return f"CAST({quote_ident(self.old)} AS {self.type.upper()})"
        return quote_ident(self.old)


class Window(BaseModel):
    """A day of one unit, clipped to the unit's span; `rows` is the old rows to copy."""

    start: int
    end: int
    rows: int


class UnitPlan(BaseModel):
    old_table: str
    old_topic: str
    new_table: str
    new_topic: str
    chain: str | None
    bound: int
    bound_from: Literal["first row", "boundary"]
    constants: dict[str, str]
    copies: list[ColumnCopy]
    filter_columns: list[str]
    live_keys: list[str]
    absent_old_columns: list[str]
    old_rows: int
    windows: list[Window]

    @property
    def rows(self) -> int:
        return sum(window.rows for window in self.windows)

    @property
    def span(self) -> tuple[int, int]:
        return self.windows[0].start, self.windows[-1].end

    @property
    def label(self) -> str:
        return f"{self.old_topic} -> {self.new_topic}"

    def value_filter(self) -> str:
        return " OR ".join(
            f"{quote_ident(column)} IS NOT NULL" for column in self.filter_columns
        )

    def old_rows_in(self, start: int, end: int) -> str:
        return (
            f"{quote_ident('topic')} = {quote_literal(self.old_topic)} "
            f'AND "timestamp" >= {timestamp_literal(start)} '
            f'AND "timestamp" < {timestamp_literal(end)} '
            f"AND ({self.value_filter()})"
        )

    def new_rows_in(self, start: int, end: int) -> str:
        return (
            f"{quote_ident('topic')} = {quote_literal(self.new_topic)} "
            f'AND "timestamp" >= {timestamp_literal(start)} '
            f'AND "timestamp" < {timestamp_literal(end)}'
        )

    def insert_sql(self, window: Window) -> str:
        targets = [
            '"timestamp"',
            *(quote_ident(column) for column in self.constants),
            *(quote_ident(copy.new) for copy in self.copies),
        ]
        sources = [
            '"timestamp"',
            *(quote_literal(value) for value in self.constants.values()),
            *(copy.expression for copy in self.copies),
        ]
        return (
            f"INSERT INTO {quote_ident(self.new_table)} ({', '.join(targets)})\n"
            f"SELECT {', '.join(sources)}\n"
            f"FROM {quote_ident(self.old_table)}\n"
            f"WHERE {self.old_rows_in(window.start, window.end)};"
        )


class Refusal(BaseModel):
    old_table: str
    old_topic: str
    new_table: str
    new_topic: str
    reason: str


class Statement(BaseModel):
    sha256: str
    table: str
    column: str | None = None
    type: str | None = None
    unit: int | None = None
    window: int | None = None


class WavePlan(BaseModel):
    wave: int
    host: str
    boundary: int
    spec_sha256: str
    sql_sha256: str
    expected_columns: dict[str, dict[str, str]]
    added_columns: dict[str, dict[str, str]]
    units: list[UnitPlan]
    refused: list[Refusal]
    statements: list[Statement]


def wave_paths(sql_path: Path) -> tuple[Path, Path, Path]:
    """The manifest, journal and check report that belong to a wave's SQL file."""
    stem = sql_path.with_suffix("")
    return (
        stem.with_suffix(".plan.json"),
        stem.with_suffix(".journal.jsonl"),
        stem.with_suffix(".check.md"),
    )


# ---- plan ------------------------------------------------------------------------------------


class _Draft(BaseModel):
    """A unit between reading Greptime and resolving its column types."""

    unit: Unit
    pairs: list[tuple[str, str]]
    filter_columns: list[str]
    live_keys: list[str]
    absent_old_columns: list[str]
    bound: int
    bound_from: Literal["first row", "boundary"]
    old_rows: int
    windows: list[Window]


def _base_columns(schema: dict[str, str]) -> set[str]:
    return {
        column.removesuffix(f"__{suffix}")
        for column in schema
        for suffix in SUFFIXES
        if column.endswith(f"__{suffix}")
    }


def _column_pairs(
    unit: Unit,
    old_schema: dict[str, str],
    new_schema: dict[str, str],
    one_to_one: bool,
) -> tuple[list[tuple[str, str]], list[str], list[str]]:
    """The (old column, new column) pairs of a unit, its live keys and its absent old columns.

    A one-to-one unit also copies every old key whose name already exists in the new table:
    node keys keep their names, so such a key is the same signal on the new topic.
    """
    mapped = [(column.old, column.new) for column in unit.columns]
    live_keys = (
        sorted(
            _base_columns(old_schema)
            & _base_columns(new_schema)
            - {old for old, _ in mapped}
            - {new for _, new in mapped}
        )
        if one_to_one
        else []
    )
    keys = [*mapped, *((key, key) for key in live_keys)]
    candidates = [
        (f"{old}__{suffix}", f"{new}__{suffix}")
        for old, new in keys
        for suffix in SUFFIXES
    ]
    pairs = [(old, new) for old, new in candidates if old in old_schema]
    absent = sorted(
        f"{column.old}__{suffix}"
        for column in unit.columns
        for suffix in column.suffixes
        if f"{column.old}__{suffix}" not in old_schema
    )
    return pairs, live_keys, absent


def _filter_columns(pairs: list[tuple[str, str]]) -> list[str]:
    values = [old for old, _ in pairs if old.endswith("__value")]
    return values or [old for old, _ in pairs]


def _day_windows(
    greptime: Greptime, unit: Unit, filter_columns: list[str], bound: int
) -> tuple[int, list[Window]]:
    condition = " OR ".join(f"{quote_ident(c)} IS NOT NULL" for c in filter_columns)
    days = greptime.rows(
        "SELECT CAST(date_trunc('day', \"timestamp\") AS BIGINT), count(*), "
        f"sum(CASE WHEN {condition} THEN 1 ELSE 0 END), "
        f'CAST(min(CASE WHEN {condition} THEN "timestamp" END) AS BIGINT), '
        f'CAST(max(CASE WHEN {condition} THEN "timestamp" END) AS BIGINT) '
        f"FROM {quote_ident(unit.old_table)} "
        f"WHERE {quote_ident('topic')} = {quote_literal(unit.old_topic)} "
        f'AND "timestamp" < {timestamp_literal(bound)} '
        "GROUP BY 1 ORDER BY 1"
    )
    old_rows = sum(int(all_rows) for _, all_rows, _, _, _ in days)
    copied = [
        (int(d), int(n), int(first), int(last)) for d, _, n, first, last in days if n
    ]
    if not copied:
        return old_rows, []
    span_start = copied[0][2]
    span_end = copied[-1][3] + 1
    windows = [
        Window(start=max(day, span_start), end=min(day + DAY_NS, span_end), rows=rows)
        for day, rows, _, _ in copied
    ]
    return old_rows, windows


def _refusal(unit: Unit, reason: str) -> Refusal:
    return Refusal(
        old_table=unit.old_table,
        old_topic=unit.old_topic,
        new_table=unit.new_table,
        new_topic=unit.new_topic,
        reason=reason,
    )


def _overlapping(drafts: list[_Draft]) -> dict[int, str]:
    """Units of one new topic whose spans overlap, by draft index: their rows would mix."""
    by_topic: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, draft in enumerate(drafts):
        if draft.windows:
            by_topic[(draft.unit.new_table, draft.unit.new_topic)].append(index)
    refused: dict[int, str] = {}
    for indices in by_topic.values():
        ordered = sorted(indices, key=lambda i: drafts[i].windows[0].start)
        for before, after in zip(ordered, ordered[1:], strict=False):
            if drafts[after].windows[0].start < drafts[before].windows[-1].end:
                for index in (before, after):
                    others = sorted(
                        drafts[i].unit.old_topic for i in indices if i != index
                    )
                    refused[index] = (
                        f"Its period overlaps another old topic of {drafts[index].unit.new_topic}: "
                        f"{', '.join(others)}"
                    )
    return refused


def _resolve(
    pairs: list[tuple[str, str]], old_schema: dict[str, str], new_types: dict[str, str]
) -> tuple[list[ColumnCopy], dict[str, str]] | str:
    """The typed column copies of a unit and the columns it adds, or why it can't be copied.

    `new_types` is the new table's columns, including those earlier units add.
    """
    copies = []
    added: dict[str, str] = {}
    for old, new in pairs:
        old_type = old_schema[old]
        new_type = new_types.get(new) or added.get(new)
        if new_type is None:
            added[new] = old_type
            copies.append(ColumnCopy(old=old, new=new, type=old_type, cast=False))
        elif new_type == old_type:
            copies.append(ColumnCopy(old=old, new=new, type=new_type, cast=False))
        elif (old_type, new_type) in LOSSLESS_CASTS:
            copies.append(ColumnCopy(old=old, new=new, type=new_type, cast=True))
        else:
            return (
                f"{old} is {old_type} and {new} is {new_type}: a cast would lose values"
            )
    return copies, added


def plan_migration(
    greptime: Greptime,
    spec: MigrationSpec,
    spec_sha256: str,
    host: str,
    boundary: int,
    old_tables: Iterable[str],
    out_dir: Path,
) -> list[Path]:
    """Write the SQL file, manifest and report of each wave of the spec's units."""
    overwritten = sorted({unit.new_table for unit in spec.units} & spec.old_tables)
    if overwritten:
        raise MigrationRefused(f"New tables that are also old tables: {overwritten}")
    selected_tables = set(old_tables)
    units = [
        unit
        for unit in spec.units
        if not selected_tables or unit.old_table in selected_tables
    ]
    unknown = selected_tables - spec.old_tables
    if unknown:
        raise MigrationRefused(f"Not an old table of the spec: {sorted(unknown)}")

    present = greptime.tables()
    involved = sorted({u.old_table for u in units} | {u.new_table for u in units})
    schemas = {table: greptime.columns(table) for table in involved if table in present}
    first_rows = {
        table: {
            topic: int(first)
            for topic, first in greptime.rows(
                f'SELECT {quote_ident("topic")}, CAST(min("timestamp") AS BIGINT) '
                f"FROM {quote_ident(table)} GROUP BY 1"
            )
        }
        for table in sorted({u.new_table for u in units})
        if table in present
    }
    spec_topics: dict[str, set[str]] = defaultdict(set)
    for unit in spec.units:
        spec_topics[unit.new_table].add(unit.new_topic)
    units_per_old_topic = Counter((u.old_table, u.old_topic) for u in spec.units)

    refused: list[Refusal] = []
    drafts: list[_Draft] = []
    for unit in sorted(units, key=lambda u: u.wave):
        if unit.old_table not in schemas:
            refused.append(_refusal(unit, "The old table doesn't exist"))
            continue
        if unit.new_table not in schemas:
            refused.append(_refusal(unit, "The new table doesn't exist yet"))
            continue
        foreign = sorted(
            topic
            for topic, first in first_rows[unit.new_table].items()
            if topic not in spec_topics[unit.new_table] and first < boundary
        )
        if foreign:
            refused.append(
                _refusal(
                    unit,
                    f"The new table holds rows before the boundary from topics outside "
                    f"the spec: {', '.join(foreign)}",
                )
            )
            continue
        if "topic" not in schemas[unit.new_table]:
            refused.append(_refusal(unit, "The new table has no topic column"))
            continue
        pairs, live_keys, absent = _column_pairs(
            unit,
            schemas[unit.old_table],
            schemas[unit.new_table],
            units_per_old_topic[(unit.old_table, unit.old_topic)] == 1,
        )
        if not pairs:
            refused.append(
                _refusal(unit, "None of its old columns is in the old table")
            )
            continue
        first_row = first_rows[unit.new_table].get(unit.new_topic)
        bound = boundary if first_row is None else first_row
        old_rows, windows = _day_windows(greptime, unit, _filter_columns(pairs), bound)
        drafts.append(
            _Draft(
                unit=unit,
                pairs=pairs,
                filter_columns=_filter_columns(pairs),
                live_keys=live_keys,
                absent_old_columns=absent,
                bound=bound,
                bound_from="boundary" if first_row is None else "first row",
                old_rows=old_rows,
                windows=windows,
            )
        )

    overlapping = _overlapping(drafts)
    pending: dict[str, dict[str, str]] = defaultdict(dict)
    added_in_wave: dict[int, dict[str, dict[str, str]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    plans: dict[int, list[UnitPlan]] = defaultdict(list)
    for index, draft in enumerate(drafts):
        unit = draft.unit
        if index in overlapping:
            refused.append(_refusal(unit, overlapping[index]))
            continue
        old_schema = schemas[unit.old_table]
        new_types = {**schemas[unit.new_table], **pending[unit.new_table]}
        constants = {"topic": unit.new_topic, "technical_name": unit.technical_name}
        if "table" in new_types:
            constants["table"] = unit.new_table
        identity_added = (
            {} if "technical_name" in new_types else {"technical_name": "string"}
        )
        source_type = (
            [("source_type", "source_type")]
            if "source_type" in new_types and "source_type" in old_schema
            else []
        )
        resolved = (
            _resolve([*draft.pairs, *source_type], old_schema, new_types)
            if draft.windows
            else ([], {})
        )
        if isinstance(resolved, str):
            refused.append(_refusal(unit, resolved))
            continue
        copies, added = resolved
        unit_added = {**identity_added, **added} if draft.windows else {}
        if unit_added:
            pending[unit.new_table].update(unit_added)
            added_in_wave[unit.wave][unit.new_table].update(unit_added)
        plans[unit.wave].append(
            UnitPlan(
                old_table=unit.old_table,
                old_topic=unit.old_topic,
                new_table=unit.new_table,
                new_topic=unit.new_topic,
                chain=unit.chain,
                bound=draft.bound,
                bound_from=draft.bound_from,
                constants=constants,
                copies=copies,
                filter_columns=draft.filter_columns,
                live_keys=draft.live_keys,
                absent_old_columns=draft.absent_old_columns,
                old_rows=draft.old_rows,
                windows=draft.windows,
            )
        )

    refused_by_wave: dict[int, list[Refusal]] = defaultdict(list)
    wave_of = {
        (u.old_table, u.old_topic, u.new_table, u.new_topic): u.wave for u in units
    }
    for refusal in refused:
        key = (
            refusal.old_table,
            refusal.old_topic,
            refusal.new_table,
            refusal.new_topic,
        )
        refused_by_wave[wave_of[key]].append(refusal)

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for wave in sorted({u.wave for u in units}):
        written.extend(
            _write_wave(
                out_dir,
                wave,
                host,
                boundary,
                spec_sha256,
                plans[wave],
                refused_by_wave[wave],
                {
                    t: dict(sorted(c.items()))
                    for t, c in sorted(added_in_wave[wave].items())
                },
                schemas,
                pending,
            )
        )
    return written


def _write_wave(
    out_dir: Path,
    wave: int,
    host: str,
    boundary: int,
    spec_sha256: str,
    units: list[UnitPlan],
    refused: list[Refusal],
    added: dict[str, dict[str, str]],
    schemas: dict[str, dict[str, str]],
    pending: dict[str, dict[str, str]],
) -> list[Path]:
    blocks: list[tuple[str, str]] = []
    statements: list[Statement] = []
    for table, columns in added.items():
        for column, column_type in columns.items():
            sql = (
                f"ALTER TABLE {quote_ident(table)} ADD COLUMN "
                f"{quote_ident(column)} {column_type.upper()} NULL;"
            )
            blocks.append((f"-- add {column} to {table}", sql))
            statements.append(
                Statement(
                    sha256=sha256(sql), table=table, column=column, type=column_type
                )
            )
    for unit_index, unit in enumerate(units):
        for window_index, window in enumerate(unit.windows):
            sql = unit.insert_sql(window)
            day = timestamp_literal(window.start)[1:11]
            blocks.append((f"-- unit {unit_index}: {unit.label}, {day}", sql))
            statements.append(
                Statement(
                    sha256=sha256(sql),
                    table=unit.new_table,
                    unit=unit_index,
                    window=window_index,
                )
            )

    header = (
        f"-- migrate-history wave {wave} on {host}, boundary {timestamp_literal(boundary)}\n"
        f"-- spec sha256 {spec_sha256}\n"
        f"-- {len(units)} units, {sum(len(u.windows) for u in units)} windows, "
        f"{sum(len(c) for c in added.values())} columns to add"
    )
    sql_text = "\n\n".join([header, *(f"{c}\n{s}" for c, s in blocks)]) + "\n"

    expected: dict[str, dict[str, str]] = defaultdict(dict)
    for unit in units:
        new_types = {**schemas[unit.new_table], **pending[unit.new_table]}
        if not unit.windows:
            continue
        for column in unit.constants:
            expected[unit.new_table][column] = new_types[column]
        for copy in unit.copies:
            expected[unit.new_table][copy.new] = copy.type
            expected[unit.old_table][copy.old] = schemas[unit.old_table][copy.old]
        expected[unit.old_table]["topic"] = schemas[unit.old_table]["topic"]
    manifest = WavePlan(
        wave=wave,
        host=host,
        boundary=boundary,
        spec_sha256=spec_sha256,
        sql_sha256=sha256(sql_text),
        expected_columns={
            t: dict(sorted(c.items())) for t, c in sorted(expected.items())
        },
        added_columns=added,
        units=units,
        refused=refused,
        statements=statements,
    )

    sql_path = out_dir / f"wave-{wave}.sql"
    manifest_path, _, _ = wave_paths(sql_path)
    report_path = sql_path.with_suffix(".report.md")
    sql_path.write_text(sql_text)
    manifest_path.write_text(manifest.model_dump_json(indent=1) + "\n")
    report_path.write_text(_plan_report(manifest))
    logger.info(
        "Wave %d: %d units, %d statements, %d refused -> %s",
        wave,
        len(units),
        len(statements),
        len(refused),
        sql_path,
    )
    return [sql_path, manifest_path, report_path]


def _table(header: list[str], rows: Iterable[Iterable[object]]) -> str:
    lines = [
        "| " + " | ".join(header) + " |",
        "|" + "---|" * len(header),
        *("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows),
    ]
    return "\n".join(lines)


def _moment(nanos: int) -> str:
    return timestamp_literal(nanos)[1:20] + "Z"


def _plan_report(plan: WavePlan) -> str:
    casts = [
        (index, copy.old, copy.new, copy.type)
        for index, unit in enumerate(plan.units)
        for copy in unit.copies
        if copy.cast
    ]
    sections = [
        f"# Migrate history, wave {plan.wave}",
        f"Host `{plan.host}`, boundary {_moment(plan.boundary)}, spec sha256 "
        f"`{plan.spec_sha256}`. {len(plan.units)} units copy "
        f"{sum(u.rows for u in plan.units):,} rows in {len(plan.statements)} statements.",
        f"## Refused ({len(plan.refused)})",
        _table(
            ["Old table", "Old topic", "New table", "New topic", "Reason"],
            (
                (
                    f"`{r.old_table}`",
                    f"`{r.old_topic}`",
                    f"`{r.new_table}`",
                    f"`{r.new_topic}`",
                    r.reason,
                )
                for r in plan.refused
            ),
        ),
        f"## Columns to add ({sum(len(c) for c in plan.added_columns.values())})",
        _table(
            ["Table", "Column", "Type"],
            (
                (f"`{table}`", f"`{column}`", column_type)
                for table, columns in plan.added_columns.items()
                for column, column_type in columns.items()
            ),
        ),
        f"## Casts ({len(casts)})",
        _table(
            ["Unit", "Old column", "New column", "Type"],
            ((i, f"`{o}`", f"`{n}`", t) for i, o, n, t in casts),
        ),
        f"## Units ({len(plan.units)})",
        "Old rows: all rows of the old topic before the bound. To copy: those with a mapped "
        "value. Live keys: old keys copied because the new table already has them.",
        _table(
            [
                "#",
                "Old table",
                "Old topic",
                "New table",
                "New topic",
                "Bound",
                "Old rows",
                "To copy",
                "Days",
                "Chain",
                "Live keys",
                "Not in the old table",
            ],
            (
                (
                    index,
                    f"`{u.old_table}`",
                    f"`{u.old_topic}`",
                    f"`{u.new_table}`",
                    f"`{u.new_topic}`",
                    f"{_moment(u.bound)} ({u.bound_from})",
                    f"{u.old_rows:,}",
                    f"{u.rows:,}",
                    len(u.windows),
                    u.chain or "",
                    ", ".join(f"`{k}`" for k in u.live_keys),
                    ", ".join(f"`{c}`" for c in u.absent_old_columns),
                )
                for index, u in enumerate(plan.units)
            ),
        ),
    ]
    return "\n\n".join(sections) + "\n"


# ---- execute ---------------------------------------------------------------------------------


def read_statements(sql_text: str) -> list[str]:
    """The statements of a planned SQL file, without their comment lines."""
    statements = []
    for block in sql_text.split("\n\n"):
        lines = [line for line in block.splitlines() if not line.startswith("--")]
        if lines:
            statements.append("\n".join(lines))
    return statements


def load_plan(sql_path: Path, host: str) -> tuple[WavePlan, list[str]]:
    """The manifest and statements of a planned SQL file, refused unless both are unchanged."""
    manifest_path, _, _ = wave_paths(sql_path)
    plan = WavePlan.model_validate_json(manifest_path.read_bytes())
    sql_text = sql_path.read_text()
    if sha256(sql_text) != plan.sql_sha256:
        raise MigrationRefused(
            f"{sql_path} isn't the file the plan wrote (sha256 differs)"
        )
    if host != plan.host:
        raise MigrationRefused(f"{sql_path} was planned for {plan.host}, not {host}")
    statements = read_statements(sql_text)
    if [sha256(s) for s in statements] != [s.sha256 for s in plan.statements]:
        raise MigrationRefused(f"{sql_path}'s statements don't match its manifest")
    return plan, statements


def read_journal(journal_path: Path) -> dict[int, dict[str, Any]]:
    if not journal_path.exists():
        return {}
    entries = [
        json.loads(line) for line in journal_path.read_text().splitlines() if line
    ]
    return {entry["statement"]: entry for entry in entries}


def _check_schema(greptime: Greptime, plan: WavePlan, done: set[int]) -> None:
    added_done = {
        (s.table, s.column)
        for i, s in enumerate(plan.statements)
        if s.column and i in done
    }
    problems = []
    for table, expected in plan.expected_columns.items():
        current = greptime.columns(table)
        for column, column_type in expected.items():
            to_add = column in plan.added_columns.get(table, {})
            if to_add and (table, column) not in added_done:
                if column in current:
                    problems.append(f"{table}.{column} has appeared since the plan")
            elif current.get(column) != column_type:
                problems.append(
                    f"{table}.{column} is {current.get(column) or 'missing'}, "
                    f"the plan expects {column_type}"
                )
    if problems:
        raise MigrationRefused(
            "The schema differs from the plan: " + "; ".join(problems)
        )


def execute_plan(
    greptime: Greptime,
    sql_path: Path,
    host: str,
    pause: float,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, int]:
    """Run a planned SQL file statement by statement; returns how many ended in each status."""
    plan, statements = load_plan(sql_path, host)
    _, journal_path, _ = wave_paths(sql_path)
    journal = read_journal(journal_path)
    done = {
        index
        for index, entry in journal.items()
        if entry["sha256"] == plan.statements[index].sha256
    }
    _check_schema(greptime, plan, done)
    statuses: Counter[str] = Counter()
    with journal_path.open("a") as journal_file:
        for index, (statement, sql) in enumerate(
            zip(plan.statements, statements, strict=True)
        ):
            if index in done:
                statuses["journalled"] += 1
                continue
            started = time.monotonic()
            entry = _run_statement(greptime, plan, index, statement, sql)
            entry["seconds"] = round(time.monotonic() - started, 3)
            journal_file.write(json.dumps(entry) + "\n")
            journal_file.flush()
            statuses[entry["status"]] += 1
            if entry["status"] == "copied":
                logger.info("%d/%d %s", index + 1, len(statements), entry)
                sleep(pause)
    logger.info("%s: %s", sql_path.name, dict(statuses))
    return dict(statuses)


def _run_statement(
    greptime: Greptime, plan: WavePlan, index: int, statement: Statement, sql: str
) -> dict[str, Any]:
    entry: dict[str, Any] = {"statement": index, "sha256": statement.sha256}
    if statement.unit is None or statement.window is None:
        greptime.run(sql)
        return {
            **entry,
            "status": "added",
            "table": statement.table,
            "column": statement.column,
        }
    unit = plan.units[statement.unit]
    window = unit.windows[statement.window]
    count_sql = (
        f"SELECT count(*) FROM {quote_ident(unit.new_table)} "
        f"WHERE {unit.new_rows_in(window.start, window.end)}"
    )
    located = {
        **entry,
        "unit": statement.unit,
        "new_topic": unit.new_topic,
        "start": _moment(window.start),
        "expected": window.rows,
    }
    present = greptime.count(count_sql)
    if present == window.rows:
        return {**located, "status": "present", "rows": present}
    if present:
        raise MigrationRefused(
            f"{unit.new_topic} holds {present} of {window.rows} rows from "
            f"{_moment(window.start)} to {_moment(window.end)}: a partial copy, to be "
            "cleared by hand"
        )
    greptime.run(sql)
    copied = greptime.count(count_sql)
    if copied != window.rows:
        logger.warning(
            "%s: copied %d rows, the plan counted %d", unit.label, copied, window.rows
        )
    return {**located, "status": "copied", "rows": copied}


# ---- check -----------------------------------------------------------------------------------


def _daily(rows: list[tuple[Any, ...]]) -> dict[int, int]:
    return {int(day): int(count) for day, count in rows}


def check_plan(greptime: Greptime, sql_path: Path, host: str) -> bool:
    """Compare old and new rows per unit and write the check report; True when all match."""
    plan, _ = load_plan(sql_path, host)
    _, _, report_path = wave_paths(sql_path)
    findings: list[tuple[int, str]] = []
    by_topic: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, unit in enumerate(plan.units):
        if not unit.windows:
            continue
        by_topic[(unit.new_table, unit.new_topic)].append(index)
        start, end = unit.span
        old_days = _daily(
            greptime.rows(
                "SELECT CAST(date_trunc('day', \"timestamp\") AS BIGINT), count(*) "
                f"FROM {quote_ident(unit.old_table)} WHERE {unit.old_rows_in(start, end)} "
                "GROUP BY 1"
            )
        )
        new_days = _daily(
            greptime.rows(
                "SELECT CAST(date_trunc('day', \"timestamp\") AS BIGINT), count(*) "
                f"FROM {quote_ident(unit.new_table)} WHERE {unit.new_rows_in(start, end)} "
                "GROUP BY 1"
            )
        )
        for day in sorted(set(old_days) | set(new_days)):
            if old_days.get(day, 0) != new_days.get(day, 0):
                findings.append(
                    (
                        index,
                        f"{_moment(day)[:10]}: {old_days.get(day, 0)} old rows, "
                        f"{new_days.get(day, 0)} new rows",
                    )
                )
        sampled = sorted(
            (c for c in unit.copies if c.old.endswith("__value")), key=lambda c: c.new
        )[:SAMPLED_COLUMNS]
        for copy in sampled:
            (old_stats,) = greptime.rows(
                f"SELECT count({copy.expression}), min({copy.expression}), "
                f"max({copy.expression}) FROM {quote_ident(unit.old_table)} "
                f"WHERE {unit.old_rows_in(start, end)}"
            )
            new_column = quote_ident(copy.new)
            (new_stats,) = greptime.rows(
                f"SELECT count({new_column}), min({new_column}), max({new_column}) "
                f"FROM {quote_ident(unit.new_table)} WHERE {unit.new_rows_in(start, end)}"
            )
            if old_stats != new_stats:
                findings.append(
                    (
                        index,
                        f"{copy.new}: count, min, max {old_stats} old, {new_stats} new",
                    )
                )

    for (table, topic), indices in sorted(by_topic.items()):
        bound = plan.units[indices[0]].bound
        new_rows = greptime.count(
            f"SELECT count(*) FROM {quote_ident(table)} "
            f"WHERE {quote_ident('topic')} = {quote_literal(topic)} "
            f'AND "timestamp" < {timestamp_literal(bound)}'
        )
        expected = sum(plan.units[i].rows for i in indices)
        if new_rows != expected:
            findings.append(
                (
                    indices[0],
                    f"{topic} holds {new_rows} rows before its bound, {expected} copied",
                )
            )

    checked = sum(len(indices) for indices in by_topic.values())
    summary = (
        f"All {checked} units match."
        if not findings
        else f"{len({i for i, _ in findings})} of {checked} units differ."
    )
    report = "\n\n".join(
        [
            f"# Check of migrate-history wave {plan.wave}",
            f"Host `{plan.host}`. Per unit: old rows with a mapped value against new rows, "
            f"per day within the unit's span; `count`, `min` and `max` of up to "
            f"{SAMPLED_COLUMNS} value columns; and per new topic, all rows before the bound "
            f"against the rows copied. {summary}",
            _table(
                ["#", "Unit", "Finding"],
                ((i, plan.units[i].label, finding) for i, finding in findings),
            ),
        ]
    )
    report_path.write_text(report + "\n")
    logger.info("%s -> %s", summary, report_path)
    return not findings
