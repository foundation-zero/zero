import logging
import sys
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, CliApp, CliSubCommand

from zero_greptime_data.config import (
    CURATED_TABLES_FILE,
    SNAPSHOT_DIR,
    GreptimeConnection,
)
from zero_greptime_data.snapshot import load_snapshot, snapshot_curated_tables

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        stream=sys.stdout,
    )


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


class ZeroGreptimeDataCli(BaseSettings, cli_kebab_case=True):
    """Zero Greptime Data

    Tooling for the dbt views built over GreptimeDB's dynamically-generated raw tables:
    snapshot prod's real schema into committed DDL, and replay it into a local Greptime so
    the dbt models can be developed and tested offline.
    """

    snapshot: CliSubCommand[SnapshotCmd]
    load: CliSubCommand[LoadCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)


def run() -> None:
    setup_logging()
    CliApp.run(ZeroGreptimeDataCli)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
