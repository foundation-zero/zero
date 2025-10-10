from sqlalchemy import Column, Float, Integer, String, Enum
from sqlalchemy.dialects.postgresql import ARRAY, NUMRANGE, TIMESTAMP
from sqlalchemy.orm import declarative_base

from .types import SeaState, ThrusterMode

Base = declarative_base()


class SailSetCombined(Base):  # type: ignore
    __tablename__ = "sail_sets_combined"

    id = Column(String, primary_key=True)
    name = Column(String)
    sails = Column(ARRAY(String))  # type: ignore


class Conditions(Base):  # type: ignore
    __tablename__ = "conditions"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    sea_state = Column(
        Enum(SeaState, name="sea_state", create_constraint=False), nullable=False
    )  # type: ignore
    awa = Column(NUMRANGE, nullable=False)
    aws = Column(NUMRANGE, nullable=False)
    pcs_mode_aft = Column(
        ARRAY(Enum(ThrusterMode, name="pcs_mode", create_constraint=False)),
        nullable=False,
    )  # type: ignore
    pcs_mode_fwd = Column(
        ARRAY(Enum(ThrusterMode, name="pcs_mode", create_constraint=False)),
        nullable=False,
    )  # type: ignore


class LoadCaseHistorical(Base):  # type: ignore
    __tablename__ = "load_cases_historical"

    time = Column("time", TIMESTAMP, nullable=False, primary_key=True)
    sea_state = Column(
        Enum(SeaState, name="sea_state", create_constraint=False), nullable=False
    )  # type: ignore
    awa = Column(Float, nullable=False)
    aws = Column(Float, nullable=False)
    pcs_mode_aft = Column(
        Enum(ThrusterMode, name="pcs_mode", create_constraint=False),
        nullable=False,
    )  # type: ignore
    pcs_mode_fwd = Column(
        Enum(ThrusterMode, name="pcs_mode", create_constraint=False),
        nullable=False,
    )  # type: ignore
    sails = Column(ARRAY(String), nullable=False)  # type: ignore


class ValueDefinitions(Base):  # type: ignore
    __tablename__ = "value_definitions"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    scope = Column(String, nullable=False)


class ReferenceValues(Base):  # type: ignore
    __tablename__ = "reference_values"

    id = Column(Integer, primary_key=True, index=True)
    sail_set_id = Column(String)
    condition_id = Column(String)
    mast_id = Column(String, nullable=True)
    value_definition_id = Column(String)
    value = Column(Float)
    error_too_low = Column(Float, nullable=True)
    error_too_high = Column(Float, nullable=True)
    warning_too_low = Column(Float, nullable=True)
    warning_too_high = Column(Float, nullable=True)


class Masts(Base):  # type: ignore
    __tablename__ = "masts"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
