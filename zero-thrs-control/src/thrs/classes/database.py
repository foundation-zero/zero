import logging

from sqlalchemy import Engine
from sqlalchemy.pool import NullPool
from sqlmodel import create_engine

from thrs.orchestration.config import Config

# from thrs.classes.session_manager import SessionManager

logger = logging.getLogger(__name__)


class Database:
    engine: Engine
    # sessionmanager = SessionManager()

    def __init__(self, settings: Config):
        engine_echo: bool = (
            True if logging.getLogger().getEffectiveLevel() <= logging.DEBUG else False
        )
        self._settings = settings
        self.init_engine(use_local_database=True, engine_echo=engine_echo)

    def init_engine(self, use_local_database: bool = False, engine_echo: bool = False):
        logger.debug("Initializing database engine...")
        if use_local_database:
            self.engine: Engine = create_engine(
                "sqlite:///database.db", echo=engine_echo
            ).execution_options(schema_translate_map={"thrs": None})
        else:
            # TODO: Use ASYNC engine
            self.engine: Engine = create_engine(
                self._settings.pg_url_sync,
                poolclass=NullPool,
            )

        logger.debug(
            "Database engine initialized: %s",
            self.engine.url.render_as_string(hide_password=True),
        )

    async def close(self):
        self.engine.dispose()
