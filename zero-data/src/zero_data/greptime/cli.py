import hashlib
import logging
from pathlib import Path
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field
from pydantic_settings import CliApp, CliPositionalArg, CliSubCommand

from zero_data.greptime.config import (
    CURATED_TABLES_FILE,
    SNAPSHOT_DIR,
    GreptimeConnection,
)
from zero_data.greptime.migrate_history import (
    Greptime,
    check_plan,
    execute_plan,
    plan_migration,
    to_nanos,
)
from zero_data.greptime.migration_spec import read_spec
from zero_data.greptime.snapshot import (
    connect,
    ensure_databases,
    load_snapshot,
    snapshot_curated_tables,
)

logger = logging.getLogger(__name__)


def _endpoint(connection: GreptimeConnection) -> str:
    return f"{connection.host}:{connection.pg_port}/{connection.dbname}"


def _connection(host: str | None) -> GreptimeConnection:
    connection = GreptimeConnection()
    if host is not None:
        connection = connection.model_copy(update={"host": host})
    return connection


class SnapshotCmd(BaseModel):
    """Dump the DDL of the curated raw tables into committed `.sql` files."""

    host: Annotated[
        str | None,
        Field(description="Greptime host to snapshot from (overrides GREPTIME_HOST)."),
    ] = None

    def cli_cmd(self) -> None:
        written = snapshot_curated_tables(
            _connection(self.host), SNAPSHOT_DIR, CURATED_TABLES_FILE
        )
        logger.info("Wrote %d snapshot file(s) to %s", len(written), SNAPSHOT_DIR)


class LoadCmd(BaseModel):
    """Recreate the snapshotted raw tables (empty) in a target Greptime, ready for dbt."""

    host: Annotated[
        str | None,
        Field(description="Greptime host to load into (overrides GREPTIME_HOST)."),
    ] = None

    def cli_cmd(self) -> None:
        loaded = load_snapshot(_connection(self.host), SNAPSHOT_DIR)
        logger.info("Loaded %d table(s) into %s", len(loaded), self.host or "local")


class InitCmd(BaseModel):
    """Create the databases dbt materializes into, ahead of a `dbt build` on a live tier."""

    host: Annotated[
        str | None,
        Field(description="Greptime host to initialize (overrides GREPTIME_HOST)."),
    ] = None

    def cli_cmd(self) -> None:
        with connect(_connection(self.host)) as handle:
            ensure_databases(handle)
        logger.info("Ensured dbt databases on %s", self.host or "local")


class MigratePlanCmd(BaseModel):
    """Write, per wave of a migration spec, the SQL to run, its manifest and a dry-run report.

    Only reads Greptime.
    """

    spec: CliPositionalArg[Path]
    boundary: Annotated[
        AwareDatetime,
        Field(
            description="Cut-over time, with its timezone: the bound of a new topic "
            "that has no row yet."
        ),
    ]
    out: Annotated[Path, Field(description="Directory to write the wave files to.")]
    table: Annotated[
        list[str], Field(description="Only these old tables (repeat for more).")
    ] = []
    host: Annotated[
        str | None,
        Field(description="Greptime host to plan against (overrides GREPTIME_HOST)."),
    ] = None

    def cli_cmd(self) -> None:
        connection = _connection(self.host)
        with connect(connection) as handle:
            plan_migration(
                Greptime(handle, connection.dbname),
                read_spec(self.spec),
                hashlib.sha256(self.spec.read_bytes()).hexdigest(),
                _endpoint(connection),
                to_nanos(self.boundary),
                self.table,
                self.out,
            )


class MigrateExecuteCmd(BaseModel):
    """Run a planned wave's SQL file as it is, journalling each statement; resumable."""

    sql: CliPositionalArg[Path]
    pause: Annotated[
        float, Field(description="Seconds to wait after each copied window.")
    ] = 1.0
    host: Annotated[
        str | None,
        Field(description="Greptime host to write to (overrides GREPTIME_HOST)."),
    ] = None

    def cli_cmd(self) -> None:
        connection = _connection(self.host)
        with connect(connection) as handle:
            execute_plan(
                Greptime(handle, connection.dbname),
                self.sql,
                _endpoint(connection),
                self.pause,
            )


class MigrateCheckCmd(BaseModel):
    """Compare a migrated wave's old and new rows and write the check report."""

    sql: CliPositionalArg[Path]
    host: Annotated[
        str | None,
        Field(description="Greptime host to check (overrides GREPTIME_HOST)."),
    ] = None

    def cli_cmd(self) -> None:
        connection = _connection(self.host)
        with connect(connection) as handle:
            matched = check_plan(
                Greptime(handle, connection.dbname), self.sql, _endpoint(connection)
            )
        if not matched:
            raise SystemExit(1)


class MigrateHistoryCmd(BaseModel):
    """Copy history from old tables into new ones: plan, review, execute, check."""

    plan: CliSubCommand[MigratePlanCmd]
    execute: CliSubCommand[MigrateExecuteCmd]
    check: CliSubCommand[MigrateCheckCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)


class GreptimeCmd(BaseModel):
    """Snapshot prod's Greptime schema and replay it into a local Greptime for dbt."""

    snapshot: CliSubCommand[SnapshotCmd]
    load: CliSubCommand[LoadCmd]
    init: CliSubCommand[InitCmd]
    migrate_history: CliSubCommand[MigrateHistoryCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
