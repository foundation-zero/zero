from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import Settings
from sqlalchemy import Column, Integer, String, Float

settings = Settings()

engine = create_async_engine(settings.pg_url, echo=True)
AsyncSessionLocal = async_sessionmaker(engine)


Base = declarative_base()


class ReferenceValue(Base):
    __tablename__ = "reference_values"

    id = Column(Integer, primary_key=True, index=True)
    sail_set_id = Column(String)
    condition_id = Column(String)
    mast_id = Column(String)
    value_definition_id = Column(String)
    value = Column(Float)
    error_too_low = Column(Float)
    error_too_high = Column(Float)
    warning_too_low = Column(Float)
    warning_too_high = Column(Float)
