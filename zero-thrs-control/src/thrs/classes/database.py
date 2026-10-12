import logging
import time
from asyncio import sleep
from collections.abc import Awaitable, Callable

import asyncpg
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from thrs.orchestration.config import Config

logger = logging.getLogger(__name__)


class PostgresDatabase:
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]

    def __init__(self, settings: Config):
        # Let engine echo if log level is DEBUG
        engine_echo = logging.getLogger().getEffectiveLevel() <= logging.DEBUG
        self._settings = settings
        self.init_engine(engine_echo=engine_echo)

    def init_engine(self, engine_echo: bool = False):
        logger.debug("Initializing database engine...")

        self.engine = create_async_engine(
            self._settings.pg_url,
            poolclass=NullPool,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

        logger.debug(
            "Database engine initialized: %s",
            self.engine.url.render_as_string(hide_password=True),
        )

    async def close(self):
        await self.engine.dispose()


_TRANSIENT_ERRORS = (
    OSError,
    asyncpg.CannotConnectNowError,
    asyncpg.ConnectionDoesNotExistError,
    asyncpg.ReadOnlySQLTransactionError,
)


def is_transient(exception: BaseException) -> bool:
    current: BaseException | None = exception
    while current is not None:
        if isinstance(current, _TRANSIENT_ERRORS):
            return True
        current = getattr(current, "orig", None) or current.__cause__
    return False


async def retry_transient[T](
    write: Callable[[], Awaitable[T]],
    budget_s: float = 60.0,
    first_delay_s: float = 0.5,
    max_delay_s: float = 5.0,
) -> T:
    deadline = time.monotonic() + budget_s
    delay_s = first_delay_s
    while True:
        try:
            return await write()
        except Exception as e:
            if not is_transient(e) or time.monotonic() + delay_s > deadline:
                raise
            logger.warning(
                "Transient database error, retrying in %.1fs: %r", delay_s, e
            )
            await sleep(delay_s)
            delay_s = min(delay_s * 2, max_delay_s)
