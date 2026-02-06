import contextlib
from typing import Any, AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class SessionManager:
    """Manages asynchronous DB sessions."""

    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    def initialize(self, host: str, engine_kwargs: dict[str, Any] = {}):
        if self._engine is not None:
            raise Exception("SessionManager already initialized")
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

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
            yield connection

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("SessionManager is not initialized")

        session = self._sessionmaker()
        async with session.begin():
            yield session
        # await session.close()
