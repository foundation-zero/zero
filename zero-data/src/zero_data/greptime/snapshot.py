"""Snapshot curated raw Greptime table DDL to committed `.sql` files, and replay it.

Dev/CI Greptime has no live MQTT data, so it lacks the tables prod grew organically: dump
prod's DDL via `SHOW CREATE TABLE` into committed files, then replay them into a fresh
local Greptime to recreate prod's table shapes (empty) for offline dbt development.
"""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import psycopg

from zero_data.greptime.config import (
    DBT_DATABASES,
    GreptimeConnection,
    read_curated_tables,
)

logger = logging.getLogger(__name__)


# A connection that dies silently (Greptime restarts, the network path drops) would otherwise
# leave a query waiting forever. Probes are answered by the peer's kernel, also while a long
# query runs.
_CONNECT_TIMEOUT_S = 30
_KEEPALIVE_IDLE_S = 60
_KEEPALIVE_INTERVAL_S = 10
_KEEPALIVE_COUNT = 6


def open_handle(connection: GreptimeConnection) -> "psycopg.Connection":
    """A Greptime connection over the Postgres wire endpoint, auto-committing DDL.

    A peer that stops answering fails the statement in flight with `OperationalError`.
    """
    return psycopg.connect(
        host=connection.host,
        port=connection.pg_port,
        user=connection.user,
        password=connection.password,
        dbname=connection.dbname,
        autocommit=True,
        connect_timeout=_CONNECT_TIMEOUT_S,
        keepalives=1,
        keepalives_idle=_KEEPALIVE_IDLE_S,
        keepalives_interval=_KEEPALIVE_INTERVAL_S,
        keepalives_count=_KEEPALIVE_COUNT,
    )


@contextmanager
def connect(
    connection: GreptimeConnection,
) -> Generator["psycopg.Connection"]:
    """`open_handle`, closed on exit."""
    handle = open_handle(connection)
    try:
        yield handle
    finally:
        handle.close()


def dump_table_ddl(handle: "psycopg.Connection", table: str) -> str:
    """The replayable `CREATE TABLE` DDL for one raw table, via `SHOW CREATE TABLE`.

    Greptime returns two columns (table name, create statement); we keep the statement.
    """
    with handle.cursor() as cursor:
        cursor.execute(f'SHOW CREATE TABLE "{table}"')  # pyrefly: ignore[no-matching-overload]
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
    handle: "psycopg.Connection",
    databases: tuple[str, ...] = DBT_DATABASES,
) -> None:
    """Create the databases dbt materializes into if absent."""
    with handle.cursor() as cursor:
        for database in databases:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")  # pyrefly: ignore[no-matching-overload]


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
                cursor.execute(path.read_text())  # pyrefly: ignore[no-matching-overload]
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
