"""Seam 1: the snapshot script — `(live Greptime connection) -> committed DDL files`.

Stands up a known raw table in a real local Greptime, snapshots it, and asserts the
emitted DDL. No database mocking.
"""

from pathlib import Path

import pytest

from tests.conftest import Greptime
from zero_greptime_data.config import GreptimeConnection
from zero_greptime_data.snapshot import connect, dump_table_ddl, write_snapshot

CREATE_KNOWN_TABLE = """
CREATE TABLE IF NOT EXISTS "{table}" (
  "ts" TIMESTAMP(3) NOT NULL,
  "host" STRING NULL,
  "rpm" DOUBLE NULL,
  TIME INDEX ("ts")
)
"""


def _normalize(sql: str) -> str:
    return " ".join(sql.split())


def test_snapshot_emits_replayable_ddl_for_known_table(
    connection: GreptimeConnection,
    public: Greptime,
    temp_table: str,
    tmp_path: Path,
) -> None:
    public.execute(CREATE_KNOWN_TABLE.format(table=temp_table))

    written = write_snapshot(connection.with_dbname("public"), [temp_table], tmp_path)

    assert written == [tmp_path / f"{temp_table}.sql"]
    ddl = _normalize(written[0].read_text())
    assert f'CREATE TABLE IF NOT EXISTS "{temp_table}"' in ddl
    assert '"ts" TIMESTAMP(3) NOT NULL' in ddl
    assert '"host" STRING' in ddl
    assert '"rpm" DOUBLE' in ddl
    assert 'TIME INDEX ("ts")' in ddl


def test_snapshot_ddl_recreates_the_same_table_shape(
    connection: GreptimeConnection,
    public: Greptime,
    temp_table: str,
    tmp_path: Path,
) -> None:
    """The emitted DDL is replayable: dropping and reloading yields the same columns."""
    public.execute(CREATE_KNOWN_TABLE.format(table=temp_table))
    original_columns = public.columns(temp_table, schema="public")

    snapshot_file = write_snapshot(
        connection.with_dbname("public"), [temp_table], tmp_path
    )[0]

    public.drop_table(temp_table)
    assert public.columns(temp_table, schema="public") == []

    public.execute(snapshot_file.read_text())

    assert public.columns(temp_table, schema="public") == original_columns
    assert original_columns == [
        ("ts", "timestamp(3)"),
        ("host", "string"),
        ("rpm", "double"),
    ]


def test_dump_table_ddl_rejects_unknown_table(
    connection: GreptimeConnection,
) -> None:
    missing = "zero_greptime_test_missing"
    with connect(connection.with_dbname("public")) as handle:
        # Greptime raises for an unknown table; the message names the table.
        with pytest.raises(Exception, match=missing):
            dump_table_ddl(handle, missing)
