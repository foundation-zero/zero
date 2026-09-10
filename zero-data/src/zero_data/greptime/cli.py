import logging
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_settings import CliApp, CliSubCommand

from zero_data.greptime.config import (
    CURATED_TABLES_FILE,
    SNAPSHOT_DIR,
    GreptimeConnection,
)
from zero_data.greptime.snapshot import load_snapshot, snapshot_curated_tables

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


class GreptimeCmd(BaseModel):
    """Snapshot prod's Greptime schema and replay it into a local Greptime for dbt."""

    snapshot: CliSubCommand[SnapshotCmd]
    load: CliSubCommand[LoadCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
