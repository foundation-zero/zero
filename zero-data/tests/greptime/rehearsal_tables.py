"""Create the new tables of a migration spec, empty, laid out as Vector creates them.

For rehearsals and tests only. On a live tier the new tables must come from Vector, whose
first value fixes each column's type.

    uv run python -m tests.greptime.rehearsal_tables <spec.json>
"""

import logging
from pathlib import Path

from pydantic_settings import BaseSettings, CliApp, CliPositionalArg

from zero_data.greptime.config import GreptimeConnection
from zero_data.greptime.migrate_history import Greptime, quote_ident
from zero_data.greptime.migration_spec import MigrationSpec, read_spec

logger = logging.getLogger(__name__)


def create_new_tables(greptime: Greptime, spec: MigrationSpec) -> list[str]:
    tables = sorted({unit.new_table for unit in spec.units})
    for table in tables:
        greptime.run(
            f"CREATE TABLE IF NOT EXISTS {quote_ident(table)} ("
            '"timestamp" TIMESTAMP(9) NOT NULL, "topic" STRING NULL, '
            '"technical_name" STRING NULL, TIME INDEX ("timestamp")) '
            "WITH (append_mode = 'true')"
        )
    return tables


class RehearsalTables(BaseSettings):
    """Create the spec's new tables in the Greptime that GREPTIME_HOST names."""

    spec: CliPositionalArg[Path]

    def cli_cmd(self) -> None:
        connection = GreptimeConnection()
        with Greptime(connection) as greptime:
            tables = create_new_tables(greptime, read_spec(self.spec))
        logger.info("Created %d tables on %s", len(tables), connection.host)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    CliApp.run(RehearsalTables)
