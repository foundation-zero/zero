from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import Settings
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.dialects.postgresql import NUMRANGE, ARRAY

settings = Settings()

engine = create_async_engine(settings.pg_url, echo=True)
AsyncSessionLocal = async_sessionmaker(engine)

Base = declarative_base()


class SailSetCombined(Base):
    __tablename__ = "sail_sets_combined"

    id = Column(String, primary_key=True)
    name = Column(String)
    sails = Column(ARRAY(String))


class Conditions(Base):
    __tablename__ = "conditions"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    sea_state = Column(String, nullable=False)
    awa = Column(NUMRANGE, nullable=False)
    aws = Column(NUMRANGE, nullable=False)
    pcs_mode_aft = Column(ARRAY(String), nullable=False)
    pcs_mode_fwd = Column(ARRAY(String), nullable=False)


class ValueDefinition(Base):
    __tablename__ = "value_definitions"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    unit = Column(String, nullable=False)


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
