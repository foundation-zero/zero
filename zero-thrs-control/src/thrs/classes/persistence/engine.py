from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy.dialects import postgresql

from thrs.classes.database import PostgresDatabase
from thrs.classes.persistence.module_snapshot import ModulePersistenceSnapshot
from thrs.db.models.module_persistence import ModulePersistence


class PersistentEngine(Protocol):
    """Persistence engine interface to save and load module persistence snapshots."""

    async def load(self, module_name: str) -> ModulePersistenceSnapshot | None: ...

    async def save(
        self, module_name: str, snapshot: ModulePersistenceSnapshot
    ) -> None: ...


class NoopPersistentEngine(PersistentEngine):
    """No-op persistence engine that does nothing."""

    async def load(self, module_name: str) -> ModulePersistenceSnapshot | None:
        return None

    async def save(self, module_name: str, snapshot: ModulePersistenceSnapshot) -> None:
        pass


class InMemoryPersistentEngine(PersistentEngine):
    """In-memory persistence engine for testing and local runs."""

    def __init__(
        self, initial: dict[str, ModulePersistenceSnapshot] | None = None
    ) -> None:
        self.snapshots: dict[str, ModulePersistenceSnapshot] = dict(initial or {})

    async def load(self, module_name: str) -> ModulePersistenceSnapshot | None:
        return self.snapshots.get(module_name)

    async def save(self, module_name: str, snapshot: ModulePersistenceSnapshot) -> None:
        self.snapshots[module_name] = snapshot.model_copy(deep=True)


class PostgresPersistentEngine(PersistentEngine):
    """Persistence engine for PostgreSQL database to store module persistence snapshots."""

    def __init__(self, database: PostgresDatabase) -> None:
        self._database = database

    async def load(self, module_name: str) -> ModulePersistenceSnapshot | None:
        async with self._database.session_factory() as session:
            stored = await session.get(ModulePersistence, module_name)

            if stored is None:
                return None

            return ModulePersistenceSnapshot(
                parameters=stored.parameters,
                manual_control_values=stored.manual_control_values,
                control_mode="automatic"
                if stored.automation_mode == "automatic"
                else "manual",
            )

    async def save(self, module_name: str, snapshot: ModulePersistenceSnapshot) -> None:
        statement = postgresql.insert(ModulePersistence).values(
            module_name=module_name,
            parameters=snapshot.parameters,
            manual_control_values=snapshot.manual_control_values,
            automation_mode=snapshot.control_mode,
            updated_at=datetime.now(UTC),
        )

        # Insert or update the record if it already exists
        upsert = statement.on_conflict_do_update(
            index_elements=[ModulePersistence.module_name],
            set_={
                "parameters": statement.excluded.parameters,
                "manual_control_values": statement.excluded.manual_control_values,
                "automation_mode": statement.excluded.automation_mode,
                "updated_at": statement.excluded.updated_at,
            },
        )

        async with self._database.session_factory() as session:
            await session.execute(upsert)
            await session.commit()
