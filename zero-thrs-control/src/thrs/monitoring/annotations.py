"""Notes on the monitoring timelines: the crew's own, and the ones the system leaves.

The crew writes annotations to a GreptimeDB table of their own. Parameter
changes and module alarms are read from the history the control loops already
write, and turned into annotations as they are asked for.
"""

import asyncio
import hashlib
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from itertools import pairwise
from typing import Any
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from thrs.monitoring.sources import MonitoringModule

QUERY_TIMEOUT = timedelta(seconds=20)
TABLE = "thrs__monitoring__annotations"
MAX_TEXT = 500
MAX_AUTHOR = 80

# Columns of a parameter set that say where it went, not what it holds.
_NOT_PARAMETERS = {"timestamp", "topic"}


class AnnotationKind(StrEnum):
    CREW = "crew"
    PARAMETERS = "parameters"
    ALARM = "alarm"


class ParameterChange(BaseModel, frozen=True):
    name: str
    previous: str | None
    value: str | None


class Annotation(BaseModel, frozen=True):
    id: str
    kind: AnnotationKind
    time: datetime
    text: str
    author: str | None = None
    # Set for crew annotations; the hash of the key of the browser that wrote it.
    owner: str | None = None
    changes: list[ParameterChange] = []


class AnnotationError(ValueError):
    pass


def owner_hash(owner_key: str) -> str:
    return hashlib.sha256(owner_key.encode()).hexdigest()


def _utc(timestamp: datetime) -> datetime:
    return timestamp.replace(tzinfo=UTC) if timestamp.tzinfo is None else timestamp


def _text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def parameter_annotations(
    module: MonitoringModule,
    rows: Sequence[dict[str, Any]],
    start: datetime,
) -> list[Annotation]:
    """One annotation per parameter set in the range that changed anything.

    `rows` are the sets in time order, starting with the last one before the
    range, which the first set in the range is compared with.
    """
    annotations = []
    for previous, row in pairwise(rows):
        time = _utc(row["timestamp"])
        if time < start:
            continue
        changes = [
            ParameterChange(
                name=name, previous=_text(previous.get(name)), value=_text(value)
            )
            for name, value in row.items()
            if name not in _NOT_PARAMETERS and previous.get(name) != value
        ]
        if changes:
            annotations.append(
                Annotation(
                    id=f"parameters:{module}:{time.isoformat()}",
                    kind=AnnotationKind.PARAMETERS,
                    time=time,
                    text=", ".join(change.name for change in changes),
                    changes=changes,
                )
            )
    return annotations


def alarm_annotations(
    module: MonitoringModule,
    changes: Sequence[tuple[datetime, Any]],
    start: datetime,
) -> list[Annotation]:
    """An annotation where the module alarm was raised or cleared in the range.

    `changes` are the alarm's value at its change points, starting with the
    value it opened the range with.
    """
    annotations = []
    for (_, previous), (changed_at, value) in pairwise(changes):
        time = _utc(changed_at)
        if time < start or bool(previous) == bool(value) or value is None:
            continue
        annotations.append(
            Annotation(
                id=f"alarm:{module}:{time.isoformat()}",
                kind=AnnotationKind.ALARM,
                time=time,
                text="raised" if value else "cleared",
            )
        )
    return annotations


class AnnotationStore:
    """The crew's annotations, in a GreptimeDB table created on first use."""

    def __init__(self, engine: AsyncEngine):
        self._engine = engine
        self._ready = asyncio.Lock()
        self._created = False

    async def _ensure_table(self) -> None:
        async with self._ready:
            if self._created:
                return
            await self._execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE} (
                    `timestamp` TIMESTAMP(3) TIME INDEX,
                    `annotation_id` STRING,
                    `module` STRING,
                    `author` STRING,
                    `note` STRING,
                    `owner` STRING,
                    `created_at` TIMESTAMP(3),
                    PRIMARY KEY (`annotation_id`)
                )
            """)
            self._created = True

    async def _execute(self, statement: str, parameters: dict[str, Any] | None = None):
        async with (
            asyncio.timeout(QUERY_TIMEOUT.total_seconds()),
            self._engine.connect() as connection,
        ):
            result = await connection.execute(text(statement), parameters or {})
            await connection.commit()
            return result

    async def between(
        self, module: MonitoringModule, start: datetime, end: datetime
    ) -> list[Annotation]:
        await self._ensure_table()
        result = await self._execute(
            f"""
            SELECT `timestamp`, `annotation_id`, `author`, `note`, `owner` FROM {TABLE}
            WHERE `timestamp` >= :start AND `timestamp` < :end AND `module` = :module
            ORDER BY `timestamp`
            """,  # noqa: S608 - the table name is a constant
            {"start": start, "end": end, "module": str(module)},
        )
        return [
            Annotation(
                id=row.annotation_id,
                kind=AnnotationKind.CREW,
                time=_utc(row.timestamp),
                text=row.note,
                author=row.author or None,
                owner=row.owner,
            )
            for row in result.all()
        ]

    async def add(
        self,
        module: MonitoringModule,
        time: datetime,
        note: str,
        author: str | None,
        owner_key: str,
    ) -> Annotation:
        note = note.strip()
        author = (author or "").strip() or None
        if not note:
            raise AnnotationError("An annotation needs a text")
        if len(note) > MAX_TEXT or (author and len(author) > MAX_AUTHOR):
            raise AnnotationError(
                f"Keep the text to {MAX_TEXT} and the name to {MAX_AUTHOR} characters"
            )
        if not owner_key:
            raise AnnotationError("An annotation needs an owner key")
        await self._ensure_table()
        annotation = Annotation(
            id=uuid4().hex,
            kind=AnnotationKind.CREW,
            time=_utc(time),
            text=note,
            author=author,
            owner=owner_hash(owner_key),
        )
        await self._execute(
            f"""
            INSERT INTO {TABLE}
                (`timestamp`, `annotation_id`, `module`, `author`, `note`, `owner`, `created_at`)
            VALUES (:time, :id, :module, :author, :note, :owner, :created_at)
            """,  # noqa: S608 - the table name is a constant
            {
                "time": annotation.time,
                "id": annotation.id,
                "module": str(module),
                "author": annotation.author or "",
                "note": annotation.text,
                "owner": annotation.owner,
                "created_at": datetime.now(UTC),
            },
        )
        return annotation

    async def delete(self, annotation_id: str, time: datetime, owner_key: str) -> bool:
        """Delete an annotation written from the browser holding `owner_key`."""
        await self._ensure_table()
        parameters = {"id": annotation_id, "time": _utc(time)}
        result = await self._execute(
            f"SELECT `owner` FROM {TABLE} WHERE `annotation_id` = :id AND `timestamp` = :time",  # noqa: S608
            parameters,
        )
        row = result.first()
        if row is None:
            return False
        if row.owner != owner_hash(owner_key):
            raise AnnotationError("Only the one who wrote an annotation can delete it")
        await self._execute(
            f"DELETE FROM {TABLE} WHERE `annotation_id` = :id AND `timestamp` = :time",  # noqa: S608
            parameters,
        )
        return True
