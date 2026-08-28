"""Snapshot the DDL of curated raw Greptime tables to committed `.sql`, and replay it.

The dev/CI Greptime instances have no live MQTT data, so they never grow the dynamically
inferred tables/columns that prod grew organically. This module bridges that gap: it dumps
the DDL of a curated set of prod tables via `SHOW CREATE TABLE` into committed files, and
replays those files into a fresh local Greptime to recreate prod's table shapes (empty) so
dbt models can be developed and tested offline.
"""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import psycopg2

from zero_greptime_data.config import (
    DBT_DATABASES,
    GreptimeConnection,
    read_curated_tables,
)

logger = logging.getLogger(__name__)


@contextmanager
def connect(
    connection: GreptimeConnection,
) -> Iterator["psycopg2.extensions.connection"]:
    """A Greptime connection over the Postgres wire endpoint, auto-committing DDL."""
    handle = psycopg2.connect(
        host=connection.host,
        port=connection.pg_port,
        user=connection.user,
        password=connection.password,
        dbname=connection.dbname,
    )
    handle.autocommit = True
    try:
        yield handle
    finally:
        handle.close()


def dump_table_ddl(handle: "psycopg2.extensions.connection", table: str) -> str:
    """The replayable `CREATE TABLE` DDL for one raw table, via `SHOW CREATE TABLE`.

    Greptime returns two columns (table name, create statement); we keep the statement.
    """
    with handle.cursor() as cursor:
        cursor.execute(f'SHOW CREATE TABLE "{table}"')
        row = cursor.fetchone()
    if row is None:
        raise ValueError(f"SHOW CREATE TABLE returned no rows for table {table!r}")
    return f"{row[1].rstrip()}\n"


def write_snapshot(
    connection: GreptimeConnection,
    tables: list[str],
    snapshot_dir: Path,
) -> list[Path]:
    """Dump each curated table's DDL to `{snapshot_dir}/{table}.sql`. Returns files written."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    with connect(connection) as handle:
        for table in tables:
            ddl = dump_table_ddl(handle, table)
            path = snapshot_dir / f"{table}.sql"
            path.write_text(ddl)
            logger.info("Snapshotted %s -> %s", table, path)
            written.append(path)
    return written


def ensure_databases(
    handle: "psycopg2.extensions.connection",
    databases: tuple[str, ...] = DBT_DATABASES,
) -> None:
    """Create the databases dbt needs (`greptime` landing db, `views` target) if absent."""
    with handle.cursor() as cursor:
        for database in databases:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")


def load_snapshot(connection: GreptimeConnection, snapshot_dir: Path) -> list[str]:
    """Recreate the snapshotted raw tables (empty) in a fresh Greptime, ready for dbt.

    Ensures the dbt databases exist, then replays every `.sql` file into `public`. The
    connection's `dbname` is forced to `public` — that is where the raw tables live.
    Returns the table names loaded.
    """
    loaded: list[str] = []
    with connect(connection.with_dbname("public")) as handle:
        ensure_databases(handle)
        with handle.cursor() as cursor:
            for path in sorted(snapshot_dir.glob("*.sql")):
                cursor.execute(path.read_text())
                logger.info("Loaded %s", path.name)
                loaded.append(path.stem)
    return loaded


def snapshot_curated_tables(
    connection: GreptimeConnection,
    snapshot_dir: Path,
    tables_file: Path,
) -> list[Path]:
    """Snapshot the curated table list (from `tables_file`) out of `connection`."""
    tables = read_curated_tables(tables_file)
    logger.info(
        "Snapshotting %d curated table(s) from %s", len(tables), connection.host
    )
    return write_snapshot(connection, tables, snapshot_dir)
