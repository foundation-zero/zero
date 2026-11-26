import logging
from contextlib import ExitStack
from datetime import date
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_settings import (
    CliApp,
    CliImplicitFlag,
    CliPositionalArg,
    CliSubCommand,
)

from zero_data.greptime.config import (
    CURATED_TABLES_FILE,
    SNAPSHOT_DIR,
    GreptimeConnection,
)
from zero_data.greptime.migrate_history import (
    Greptime,
    check,
    drop,
    leftover,
    load,
    lock,
    report,
    run,
)
from zero_data.greptime.migration_spec import build_spec, read_mapping, read_spec
from zero_data.greptime.snapshot import (
    connect,
    ensure_databases,
    load_snapshot,
    snapshot_curated_tables,
)

logger = logging.getLogger(__name__)


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


class _MigrateCmd(BaseModel):
    spec: CliPositionalArg[Path]
    table: Annotated[
        list[str],
        Field(
            description="Only the new topics these old tables feed (repeat for more). "
            "Other old tables that feed the same topics come along."
        ),
    ] = []
    host: Annotated[
        str | None,
        Field(description="Greptime host (overrides GREPTIME_HOST)."),
    ] = None


class MigrateBuildSpecCmd(BaseModel):
    """Turn a mapping of old and new topics and keys into a spec, by running Vector in Docker."""

    mapping: CliPositionalArg[Path]
    out: Annotated[Path, Field(description="The spec file to write.")]

    def cli_cmd(self) -> None:
        spec = build_spec(read_mapping(self.mapping))
        self.out.write_text(spec.model_dump_json(indent=1))
        logger.info("Wrote %d units to %s", len(spec.units), self.out)


class MigrateRunCmd(_MigrateCmd):
    """Copy the history day by day, newest first. Safe to stop and to run again."""

    until: Annotated[
        date | None,
        Field(description="Copy back to and including this day (default: everything)."),
    ] = None
    from_: Annotated[
        date | None,
        Field(
            alias="from",
            description="Start at this day and leave newer days alone, so a restart "
            "reads only the days still to copy (default: every day).",
        ),
    ] = None
    dry_run: Annotated[
        CliImplicitFlag[bool],
        Field(description="Only read, and print what a run would do."),
    ] = False
    pause: Annotated[
        float,
        Field(
            description="Seconds to wait after each copied topic and day, to leave "
            "room for live data. A system has some 80,000 of them."
        ),
    ] = 0.1
    unlock: Annotated[
        CliImplicitFlag[bool],
        Field(description="Clear the lock an interrupted run left behind, then run."),
    ] = False

    def cli_cmd(self) -> None:
        connection = _connection(self.host)
        spec = read_spec(self.spec)
        with Greptime(connection) as greptime:
            if self.dry_run:
                leftovers = {
                    table: leftover(greptime, spec, table)
                    for table in self.table or spec.old_tables
                    if table in greptime.tables()
                }
                print(
                    report(
                        load(greptime, spec, self.table, up_to=self.from_), leftovers
                    )
                )
                return
            with (
                Greptime(connection) as lock_greptime,
                lock(lock_greptime, self.unlock),
            ):
                migration = load(greptime, spec, self.table, up_to=self.from_)
                for refusal in migration.refused:
                    logger.warning(
                        "Left out %s: %s", refusal.unit.label, refusal.reason
                    )
                copied = run(greptime, migration, self.until, self.pause)
        logger.info("Copied %d rows", copied)


class MigrateCheckCmd(_MigrateCmd):
    """Compare the old and new rows of every unit; exits 1 when they differ."""

    from_: Annotated[
        date | None,
        Field(
            alias="from",
            description="Check only this day and older.",
        ),
    ] = None
    days_only: Annotated[
        CliImplicitFlag[bool],
        Field(
            description="Compare only the rows per day, not the values of every column."
        ),
    ] = False

    def cli_cmd(self) -> None:
        connection = _connection(self.host)
        with Greptime(connection) as greptime:
            migration = load(greptime, read_spec(self.spec), self.table, self.from_)
            findings = check(greptime, migration, days_only=self.days_only)
        for finding in findings:
            print(finding)
        if findings:
            raise SystemExit(1)
        logger.info("Old and new match")


class MigrateDropCmd(_MigrateCmd):
    """Drop the old tables whose history is checked. Prints what it would do unless --execute."""

    accept_unmigrated: Annotated[
        CliImplicitFlag[bool],
        Field(description="Also drop the named tables that hold data no unit copies."),
    ] = False
    execute: Annotated[CliImplicitFlag[bool], Field(description="Drop the tables.")] = (
        False
    )
    unlock: Annotated[
        CliImplicitFlag[bool],
        Field(description="Clear the lock an interrupted run left behind, then drop."),
    ] = False

    def cli_cmd(self) -> None:
        if self.accept_unmigrated and not self.table:
            raise SystemExit("--accept-unmigrated needs the tables named with --table")
        connection = _connection(self.host)
        with Greptime(connection) as greptime, ExitStack() as held:
            if self.execute:
                lock_greptime = held.enter_context(Greptime(connection))
                held.enter_context(lock(lock_greptime, self.unlock))
            outcomes = drop(
                greptime,
                read_spec(self.spec),
                self.table,
                self.accept_unmigrated,
                self.execute,
            )
        for table, outcome in outcomes.items():
            print(f"{table}: {outcome}")


class MigrateHistoryCmd(BaseModel):
    """Copy history from old tables into renamed ones, check it, and drop the old tables."""

    build_spec: CliSubCommand[MigrateBuildSpecCmd]
    run: CliSubCommand[MigrateRunCmd]
    check: CliSubCommand[MigrateCheckCmd]
    drop: CliSubCommand[MigrateDropCmd]

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
