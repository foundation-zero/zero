from datetime import UTC, date

import aiomysql
from pydantic import SecretStr

from zero_alert_forwarder.alert import Alert

NO_SUCH_TABLE = 1146


class MysqlDayTables:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: SecretStr,
        database: str,
    ):
        self.name = f"{host}:{port}/{database}"
        self._connection_args = {
            "host": host,
            "port": port,
            "user": user,
            "password": password.get_secret_value(),
            "db": database,
            "autocommit": True,
            # The AMCS database is not ours to write to, so refuse to even try.
            "init_command": "SET SESSION TRANSACTION READ ONLY",
        }

    async def latest_id(self, day: date) -> int:
        rows = await self._query(f"SELECT MAX(id) AS id FROM {_table(day)}", day)
        return (rows[0]["id"] or 0) if rows else 0

    async def read_after(self, day: date, after_id: int) -> list[Alert]:
        rows = await self._query(
            "SELECT id, eventTime, priority, `update`, `system`, tag, location, description"
            f" FROM {_table(day)} WHERE id > %s ORDER BY id",
            day,
            after_id,
        )
        return [_alert(row) for row in rows]

    async def _query(self, sql: str, day: date, *args: int) -> list[dict]:
        async with aiomysql.connect(**self._connection_args) as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                try:
                    await cursor.execute(sql, args)
                except aiomysql.ProgrammingError as error:
                    # The table of a day only exists once the AMCS raised its first alert.
                    if error.args[0] == NO_SUCH_TABLE:
                        return []
                    raise
                return list(await cursor.fetchall())


def _table(day: date) -> str:
    return f"`{day:%Y/%m/%d}`"


def _alert(row: dict) -> Alert:
    return Alert(
        id=row["id"],
        event_time=row["eventTime"].replace(tzinfo=UTC),
        priority=row["priority"],
        update=row["update"],
        system=row["system"],
        tag=row["tag"],
        location=row["location"],
        description=row["description"],
    )
