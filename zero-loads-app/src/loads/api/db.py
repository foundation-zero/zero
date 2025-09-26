import contextlib
from typing import Any, AsyncIterator

from loads.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class SessionManager:
    """Manages asynchronous DB sessions with connection pooling."""

    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine: AsyncEngine | None = create_async_engine(host, **engine_kwargs)
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = (
            async_sessionmaker(autocommit=False, bind=self._engine)
        )

    async def close(self):
        if self._engine is None:
            raise Exception("SessionManager is not initialized")
        engine = self._engine
        self._engine = None
        self._sessionmaker = None
        await engine.dispose()

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("SessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("SessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = SessionManager(settings.pg_url, engine_kwargs={"echo": False})


async def get_db_session():
    if sessionmanager is None:
        raise RuntimeError("SessionManager not initialized")
    async with sessionmanager.session() as session:
        yield session
