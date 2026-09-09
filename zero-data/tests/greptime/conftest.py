"""Shared fixtures for the Greptime integration tests.

Tests run against a real local GreptimeDB (repo-root docker-compose, PG endpoint :4003) —
the project is database glue, so mocking would test nothing. Greptime must already be up
and reachable via `GREPTIME_*` env (default `127.0.0.1:4003`), as CI provides it.
"""

from collections.abc import Iterator
from typing import Any

import pytest

from zero_data.greptime.config import GreptimeConnection
from zero_data.greptime.snapshot import connect


@pytest.fixture
def connection() -> GreptimeConnection:
    return GreptimeConnection()


class Greptime:
    """A thin query helper bound to one Greptime database, for arranging and asserting."""

    def __init__(self, connection: GreptimeConnection, dbname: str) -> None:
        self._connection = connection.with_dbname(dbname)

    def execute(self, sql: str) -> None:
        with connect(self._connection) as handle, handle.cursor() as cursor:
            cursor.execute(sql)

    def fetch(self, sql: str) -> list[tuple[Any, ...]]:
        with connect(self._connection) as handle, handle.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def column_names(self, sql: str) -> list[str]:
        """The result columns of a query, read from the cursor description.

        Greptime does not populate `information_schema.columns` for views, so this is how we
        read a view's actual output columns.
        """
        with connect(self._connection) as handle, handle.cursor() as cursor:
            cursor.execute(sql)
            description = cursor.description
            assert description is not None
            return [column.name for column in description]

    def columns(self, table: str, schema: str) -> list[tuple[str, str]]:
        """`(column_name, data_type)` pairs for a table, in declaration order."""
        rows = self.fetch(
            "select column_name, data_type from information_schema.columns "
            f"where table_schema = '{schema}' and table_name = '{table}' "
            "order by ordinal_position"
        )
        return [(name, data_type) for name, data_type in rows]

    def drop_table(self, table: str) -> None:
        self.execute(f'DROP TABLE IF EXISTS "{table}"')


@pytest.fixture
def public(connection: GreptimeConnection) -> Greptime:
    """Query helper against the raw-ingest `public` database."""
    return Greptime(connection, "public")


@pytest.fixture
def temp_table(public: Greptime) -> Iterator[str]:
    """A distinctive table name in `public`, dropped before and after the test."""
    table = "zero_greptime_test_engine"
    public.drop_table(table)
    try:
        yield table
    finally:
        public.drop_table(table)
