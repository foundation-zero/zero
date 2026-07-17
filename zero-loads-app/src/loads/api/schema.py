from typing import Sequence

from sqlalchemy import Column, Float, ForeignKey, Integer, MetaData, String
from sqlalchemy.dialects.postgresql import ARRAY, NUMRANGE, UUID
from sqlalchemy.orm import DeclarativeBase, relationship

metadata_obj = MetaData(schema="loads")


class Base(DeclarativeBase):
    metadata = metadata_obj


class SailPositions(Base):
    __tablename__ = "sail_positions"
    id = Column(String, primary_key=True)


class Sails(Base):
    __tablename__ = "sails"
    id = Column(String, primary_key=True)
    abbreviation = Column(String, nullable=False)
    position_id = Column(String, ForeignKey("sail_positions.id"), nullable=False)
    name = Column(String, nullable=False)
    variant_name = Column(String, nullable=False)


class SailSets(Base):
    __tablename__ = "sail_sets"

    sail_set_id = Column(Integer, primary_key=True)
    position_id = Column(String, ForeignKey("sail_positions.id"), primary_key=True)
    sail_id = Column(String, ForeignKey("sails.id"), nullable=True)


class SailSetsCombined(Base):
    __tablename__ = "sail_sets_combined"

    id = Column(Integer, primary_key=True)
    sails: Column[Sequence[str]] = Column(ARRAY(String), nullable=False)


class AwaRanges(Base):
    __tablename__ = "awa_ranges"

    id = Column(String, primary_key=True)
    awa_range = Column(NUMRANGE, nullable=False)


class AwsRanges(Base):
    __tablename__ = "aws_ranges"

    id = Column(Integer, primary_key=True)
    aws_range = Column(NUMRANGE, nullable=False)


class LoadCases(Base):
    __tablename__ = "load_cases"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    awa = Column(Float, nullable=False)
    aws = Column(Float, nullable=False)
    sail_set_id = Column(Integer, nullable=False, index=True)


class ReferenceValues(Base):
    __tablename__ = "reference_values"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()"
    )
    load_case_id = Column(
        String, ForeignKey("load_cases.id"), nullable=False, index=True
    )
    variable_key = Column(String, nullable=False)
    alarm_low = Column(Float, nullable=True)
    warning_low = Column(Float, nullable=True)
    target = Column(Float, nullable=True)
    warning_high = Column(Float, nullable=True)
    alarm_high = Column(Float, nullable=True)

    load_case = relationship("LoadCases")


class LoadCaseMappings(Base):
    __tablename__ = "load_case_mappings"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()"
    )
    load_case_id = Column(
        String, ForeignKey("load_cases.id"), nullable=False, index=True
    )
    awa_range_id = Column(String, ForeignKey("awa_ranges.id"), nullable=False)
    aws_range_id = Column(Integer, ForeignKey("aws_ranges.id"), nullable=False)
    sail_set_id = Column(Integer, nullable=False)

    load_case = relationship("LoadCases")
