from sqlalchemy import Column, Float, ForeignKey, Integer, MetaData, String
from sqlalchemy.dialects.postgresql import ARRAY, NUMRANGE, UUID
from sqlalchemy.orm import declarative_base, relationship

metadata_obj = MetaData(schema="loads")

Base = declarative_base(metadata=metadata_obj)


class Sails(Base):
    __tablename__ = "sails"
    id = Column(String, primary_key=True)
    abbreviation = Column(String, nullable=False)
    position_id = Column(String, nullable=False)
    name = Column(String, nullable=False)


class SailSets(Base):
    __tablename__ = "sail_sets"

    id = Column(Integer, primary_key=True)
    main_sail_id = Column(String, ForeignKey("sails.id"), nullable=True, index=True)
    mizzen_sail_id = Column(String, ForeignKey("sails.id"), nullable=True, index=True)
    fore_inner_sail_id = Column(
        String, ForeignKey("sails.id"), nullable=True, index=True
    )
    fore_outer_sail_id = Column(
        String, ForeignKey("sails.id"), nullable=True, index=True
    )
    mizzen_fore_sail_id = Column(
        String, ForeignKey("sails.id"), nullable=True, index=True
    )
    sail_set = Column(ARRAY(String))

    main_sail = relationship("Sails", foreign_keys=[main_sail_id])
    mizzen_sail = relationship("Sails", foreign_keys=[mizzen_sail_id])
    fore_inner_sail = relationship("Sails", foreign_keys=[fore_inner_sail_id])
    fore_outer_sail = relationship("Sails", foreign_keys=[fore_outer_sail_id])
    mizzen_fore_sail = relationship("Sails", foreign_keys=[mizzen_fore_sail_id])


class TwaRanges(Base):
    __tablename__ = "twa_ranges"

    id = Column(Integer, primary_key=True)
    twa = Column(NUMRANGE, nullable=False)


class TwsRanges(Base):
    __tablename__ = "tws_ranges"

    id = Column(Integer, primary_key=True)
    tws = Column(NUMRANGE, nullable=False)


class LoadCases(Base):
    __tablename__ = "load_cases"

    id = Column(Integer, primary_key=True)
    twa_range_id = Column(
        Integer, ForeignKey("twa_ranges.id"), nullable=False, index=True
    )
    tws_range_id = Column(
        Integer, ForeignKey("tws_ranges.id"), nullable=False, index=True
    )
    sail_set_id = Column(
        Integer, ForeignKey("sail_sets.id"), nullable=False, index=True
    )

    twa_range = relationship("TwaRanges")
    tws_range = relationship("TwsRanges")
    sail_set = relationship("SailSets")


class Variables(Base):
    __tablename__ = "variables"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)


class ReferenceValues(Base):
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
