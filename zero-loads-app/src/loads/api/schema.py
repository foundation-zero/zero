from typing import Sequence

from sqlalchemy import Column, Float, ForeignKey, Integer, MetaData, String
from sqlalchemy.dialects.postgresql import ARRAY, NUMRANGE, UUID
from sqlalchemy.orm import declarative_base, relationship

metadata_obj = MetaData(schema="loads")

Base = declarative_base(metadata=metadata_obj)


class SailPositions(Base):  # type:ignore
    __tablename__ = "sail_positions"
    id = Column(String, primary_key=True)


class Sails(Base):  # type:ignore
    __tablename__ = "sails"
    id = Column(String, primary_key=True)
    abbreviation = Column(String, nullable=False)
    position_id = Column(String, ForeignKey("sail_positions.id"), nullable=False)
    name = Column(String, nullable=False)


class SailSets(Base):  # type:ignore
    __tablename__ = "sail_sets"

    sail_set_id = Column(Integer, primary_key=True)
    position_id = Column(String, ForeignKey("sail_positions.id"), primary_key=True)
    sail_id = Column(String, ForeignKey("sails.id"), nullable=True)


class SailSetsCombined(Base):  # type:ignore
    __tablename__ = "sail_sets_combined"

    id = Column(Integer, primary_key=True)
    sails: Column[Sequence[str]] = Column(ARRAY(String), nullable=False)


class AwaRanges(Base):  # type:ignore
    __tablename__ = "awa_ranges"

    id = Column(Integer, primary_key=True)
    awa = Column(NUMRANGE, nullable=False)


class AwsRanges(Base):  # type:ignore
    __tablename__ = "aws_ranges"

    id = Column(Integer, primary_key=True)
    aws = Column(NUMRANGE, nullable=False)


class LoadCases(Base):  # type:ignore
    __tablename__ = "load_cases"

    id = Column(UUID(as_uuid=True), primary_key=True)
    awa_range_id = Column(
        Integer, ForeignKey("awa_ranges.id"), nullable=False, index=True
    )
    aws_range_id = Column(
        Integer, ForeignKey("aws_ranges.id"), nullable=False, index=True
    )
    sail_set_id = Column(Integer, nullable=False, index=True)

    awa_range = relationship("AwaRanges")
    aws_range = relationship("AwsRanges")


class Variables(Base):  # type: ignore
    __tablename__ = "variables"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    minimum_value = Column(Float, nullable=True)
    maximum_value = Column(Float, nullable=True)
    tag = Column(String, nullable=True)


class ReferenceValues(Base):  # type:ignore
    __tablename__ = "reference_values"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()"
    )
    load_case_id = Column(
        Integer, ForeignKey("load_cases.id"), nullable=False, index=True
    )
    variable_id = Column(String, ForeignKey("variables.id"), nullable=False, index=True)
    alarm_low = Column(Float, nullable=True)
    warning_low = Column(Float, nullable=True)
    target = Column(Float, nullable=True)
    warning_high = Column(Float, nullable=True)
    alarm_high = Column(Float, nullable=True)

    load_case = relationship("LoadCases")
    variable = relationship("Variables")
