from sqlalchemy import Engine
from sqlmodel import create_engine
from sqlalchemy.pool import NullPool
from thrs.orchestration.config import settings


class Database:
    engine: Engine

    def __init__(self):
        self.init_engine()

    def init_engine(self):
        use_local: bool = True  # TODO: Test purpose only

        if use_local:
            self.engine: Engine = create_engine("sqlite:///database.db", echo=True)
        else:
            self.engine: Engine = create_engine(
                settings.pg_url, echo=True, poolclass=NullPool
            )


db = Database()
