import logging
from unittest import mock

import pytest
from sqlalchemy.exc import OperationalError

from tests.helpers.modules import make_module
from thrs.classes.database import PostgresDatabase
from thrs.classes.persistence.engine import (
    NoopPersistentEngine,
    PostgresPersistentEngine,
)
from thrs.orchestration.setup import setup_persistence_manager


def _connection_error() -> OperationalError:
    return OperationalError("select 1", {}, Exception("connection refused"))


class _FailingSessionFactory:
    """Stands in for `PostgresDatabase.session_factory` when Postgres can't be
    reached at all - `async with database.session_factory() as session` raises
    before a session is ever obtained."""

    def __call__(self):
        return self

    async def __aenter__(self):
        raise _connection_error()

    async def __aexit__(self, *exc_info):
        return False


class _WorkingSession:
    async def execute(self, *args, **kwargs):
        return None


class _WorkingSessionFactory:
    def __call__(self):
        return self

    async def __aenter__(self):
        return _WorkingSession()

    async def __aexit__(self, *exc_info):
        return False


def _fake_database(session_factory) -> PostgresDatabase:
    database = mock.Mock(spec=PostgresDatabase)
    database.session_factory = session_factory
    return database


async def test_falls_back_to_noop_when_postgres_is_unreachable(
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.WARNING, logger="thrs.orchestration.setup")
    database = _fake_database(_FailingSessionFactory())

    manager = await setup_persistence_manager(database, module_persistence_enabled=True)

    assert isinstance(manager._persistence_engine, NoopPersistentEngine)
    assert "not reachable" in caplog.text

    # And, concretely: no restore takes place - the module keeps its defaults.
    module = make_module()
    assert await manager.restore(module) is False
    assert module.get_persistence_snapshot().parameters == {"setpoint": 50.0}


async def test_uses_postgres_engine_when_reachable():
    database = _fake_database(_WorkingSessionFactory())

    manager = await setup_persistence_manager(database, module_persistence_enabled=True)

    assert isinstance(manager._persistence_engine, PostgresPersistentEngine)


async def test_stays_noop_when_persistence_disabled_even_if_postgres_is_up():
    database = _fake_database(_WorkingSessionFactory())

    manager = await setup_persistence_manager(
        database, module_persistence_enabled=False
    )

    assert isinstance(manager._persistence_engine, NoopPersistentEngine)


async def test_stays_noop_without_a_database():
    manager = await setup_persistence_manager(None, module_persistence_enabled=True)

    assert isinstance(manager._persistence_engine, NoopPersistentEngine)
