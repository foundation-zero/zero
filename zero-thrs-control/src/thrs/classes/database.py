import logging

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
