from types import SimpleNamespace
from unittest import mock

import pytest
from pydantic import ValidationError

from thrs.classes.database import PostgresDatabase
from thrs.classes.persistence.engine import PostgresPersistentEngine


def _stored_row(automation_mode: str) -> SimpleNamespace:
    """Stands in for a `ModulePersistence` row as returned by `session.get()`."""
    return SimpleNamespace(
        parameters={"setpoint": 60.0},
        manual_control_values=None,
        automation_mode=automation_mode,
    )


class _Session:
    def __init__(self, row: SimpleNamespace | None) -> None:
        self._row = row

    async def get(self, *args, **kwargs) -> SimpleNamespace | None:
        return self._row


class _SessionFactory:
    def __init__(self, row: SimpleNamespace | None) -> None:
        self._row = row

    def __call__(self):
        return self

    async def __aenter__(self) -> _Session:
        return _Session(self._row)

    async def __aexit__(self, *exc_info):
        return False


def _fake_database(row: SimpleNamespace | None) -> PostgresDatabase:
    database = mock.Mock(spec=PostgresDatabase)
    database.session_factory = _SessionFactory(row)
    return database


@pytest.mark.parametrize("automation_mode", ["manual", "automatic"])
async def test_load_accepts_valid_automation_modes(automation_mode: str):
    engine = PostgresPersistentEngine(_fake_database(_stored_row(automation_mode)))

    snapshot = await engine.load("dhw")

    assert snapshot is not None
    assert snapshot.control_mode == automation_mode


async def test_load_raises_on_corrupt_automation_mode():
    """A hand-edited or otherwise corrupt row must surface as a `ValidationError` -
    never be silently coerced into `manual`, which would mask real data corruption."""
    engine = PostgresPersistentEngine(_fake_database(_stored_row("deleted-enum-value")))

    with pytest.raises(ValidationError):
        await engine.load("dhw")


async def test_load_returns_none_when_nothing_is_stored():
    engine = PostgresPersistentEngine(_fake_database(None))

    assert await engine.load("dhw") is None
