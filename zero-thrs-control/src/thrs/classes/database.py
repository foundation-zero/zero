import logging

from sqlalchemy import Engine
from sqlmodel import create_engine
from sqlalchemy.pool import NullPool

# from thrs.classes.session_manager import SessionManager
from thrs.orchestration.config import settings


class Database:
    engine: Engine
    # sessionmanager = SessionManager()

    def __init__(self):
        logging.getLogger().setLevel(logging.DEBUG)  # TODO: REMOVE
        engine_echo: bool = (
            True if logging.getLogger().getEffectiveLevel() <= logging.DEBUG else False
        )
        self.init_engine(engine_echo=engine_echo)

    def init_engine(self, use_local_database: bool = False, engine_echo: bool = False):
        if use_local_database:
            self.engine: Engine = create_engine(
                "sqlite:///database.db", echo=engine_echo
            )
        else:
            # TODO: Use ASYNC engine
            self.engine: Engine = create_engine(
                settings.pg_url_sync,
                poolclass=NullPool,
            )

    async def close(self):
        self.engine.dispose()


db = Database()
