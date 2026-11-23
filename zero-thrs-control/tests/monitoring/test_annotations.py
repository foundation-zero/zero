import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from secrets import token_hex

import pytest
from sqlalchemy import text

from thrs.monitoring.annotations import (
    AnnotationError,
    AnnotationKind,
    AnnotationStore,
    alarm_annotations,
    owner_hash,
    parameter_annotations,
)
from thrs.monitoring.history import create_engine
from thrs.monitoring.sources import MonitoringModule

START = datetime(2026, 11, 10, 12, tzinfo=UTC)
END = START + timedelta(hours=1)


def at(minutes: float) -> datetime:
    return START + timedelta(minutes=minutes)


def test_parameter_sets_become_annotations_of_what_changed():
    rows = [
        {
            "timestamp": at(-90),
            "topic": "t",
            "minimum_tank_temperature": 55.0,
            "tank_1_enabled": 1,
        },
        {
            "timestamp": at(5),
            "topic": "t",
            "minimum_tank_temperature": 55.0,
            "tank_1_enabled": 1,
        },
        {
            "timestamp": at(10),
            "topic": "t",
            "minimum_tank_temperature": 40.0,
            "tank_1_enabled": 0,
        },
    ]

    [annotation] = parameter_annotations(MonitoringModule.DHW, rows, START)

    assert annotation.kind == AnnotationKind.PARAMETERS
    assert annotation.time == at(10)
    assert annotation.text == "minimum_tank_temperature, tank_1_enabled"
    assert [(c.name, c.previous, c.value) for c in annotation.changes] == [
        ("minimum_tank_temperature", "55", "40"),
        ("tank_1_enabled", "1", "0"),
    ]


def test_parameter_sets_before_the_range_are_only_compared_with():
    rows = [
        {"timestamp": at(-20), "topic": "t", "minimum_tank_temperature": 50.0},
        {"timestamp": at(-10), "topic": "t", "minimum_tank_temperature": 55.0},
    ]
    assert parameter_annotations(MonitoringModule.DHW, rows, START) == []


def test_alarms_become_annotations_where_raised_or_cleared():
    changes = [(at(-5), False), (at(10), True), (at(12), True), (at(20), False)]

    annotations = alarm_annotations(MonitoringModule.DHW, changes, START)

    assert [(a.time, a.text) for a in annotations] == [
        (at(10), "raised"),
        (at(20), "cleared"),
    ]
    assert {a.kind for a in annotations} == {AnnotationKind.ALARM}


@pytest.fixture
async def store() -> AsyncIterator[AnnotationStore]:
    base_url = os.environ.get("GREPTIME_TEST_URL", "mysql://localhost:14002/public")
    database = f"thrs_annotations_test_{token_hex(4)}"
    admin = create_engine(base_url)
    engine = create_engine(f"{base_url.rsplit('/', 1)[0]}/{database}")
    try:
        async with admin.connect() as connection:
            await connection.execute(text(f"CREATE DATABASE {database}"))
        yield AnnotationStore(engine)
    finally:
        await engine.dispose()
        async with admin.connect() as connection:
            await connection.execute(text(f"DROP DATABASE IF EXISTS {database}"))
        await admin.dispose()


@pytest.mark.greptime
async def test_crew_annotations_are_kept_per_module(store):
    added = await store.add(
        MonitoringModule.DHW, at(10), " Swapped tank 2 sensor ", "Erik", "key-a"
    )

    [found] = await store.between(MonitoringModule.DHW, START, END)

    assert found.id == added.id
    assert found.time == at(10)
    assert found.text == "Swapped tank 2 sensor"
    assert found.author == "Erik"
    assert found.owner == owner_hash("key-a")
    assert await store.between(MonitoringModule.DHW, at(20), END) == []


@pytest.mark.greptime
async def test_only_the_writing_browser_deletes_an_annotation(store):
    added = await store.add(MonitoringModule.DHW, at(10), "Note", None, "key-a")

    with pytest.raises(AnnotationError):
        await store.delete(added.id, added.time, "key-b")
    assert await store.delete(added.id, added.time, "key-a")

    assert await store.between(MonitoringModule.DHW, START, END) == []
    assert not await store.delete(added.id, added.time, "key-a")


@pytest.mark.greptime
async def test_an_annotation_needs_a_text(store):
    with pytest.raises(AnnotationError):
        await store.add(MonitoringModule.DHW, at(10), "  ", None, "key-a")
