import logging
from typing import Sequence

from sqlalchemy import Column, Subquery, cast, literal, or_, select, text
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.sql.selectable import ScalarSelect
from strawberry import ID

from loads.registry.registry import VARIABLES, VariableDefinition

from .schema import (
    AwaRanges,
    AwsRanges,
    LoadCases,
    ReferenceValues,
    SailSetsCombined,
)
from .schema import (
    Sails as SailsTable,
)
from .types import (
    AwaRange,
    AwsRange,
    CaseInput,
    ReferenceValue,
    ReferenceValueInput,
    SailType,
    Unit,
    VariableType,
)

logger = logging.getLogger("api")


async def get_loads_reference_values(
    variables: list[str],
    case: CaseInput,
    session: AsyncSession,
) -> list[ReferenceValue]:
    """Return all reference values that match the current sails and conditions."""

    query = (
        select(ReferenceValues)
        .where(ReferenceValues.variable_id.in_(variables))
        .where(
            ReferenceValues.load_case.has(
                LoadCases.awa_range.has(AwaRanges.id == case.awa_range.value)
            )
        )
        .where(
            ReferenceValues.load_case.has(
                LoadCases.aws_range.has(
                    AwsRanges.aws_range == text(f"'{case.aws_range.value}'::numrange")
                )
            )
        )
        .where(
            ReferenceValues.load_case.has(
                LoadCases.sail_set_id == create_sail_set_subq(case.sailset)
            )
        )
    )

    result = await session.execute(query)
    reference_values = result.scalars().all()

    if reference_values:
        return [
            ReferenceValue(
                id=ref_value.variable_id,  # type: ignore
                alarm_low=ref_value.alarm_low,  # type: ignore
                warning_low=ref_value.warning_low,  # type: ignore
                target=ref_value.target,  # type: ignore
                warning_high=ref_value.warning_high,  # type: ignore
                alarm_high=ref_value.alarm_high,  # type: ignore
            )
            for ref_value in reference_values
        ]
    else:
        logger.info(f"No reference values found for case: {case}")
        return []


async def set_loads_reference_values(
    reference_value: ReferenceValueInput,
    sail_set: Sequence[str],
    awa_ranges: list[AwaRange],
    aws_ranges: list[AwsRange],
    session: AsyncSession,
):
    """Insert or update reference values for a variable across multiple sail sets and conditions."""

    load_case_subquery = create_load_case_subq(awa_ranges, aws_ranges, sail_set)

    insert_statement = insert(ReferenceValues).from_select(
        [
            ReferenceValues.load_case_id,
            ReferenceValues.variable_id,
            ReferenceValues.alarm_low,
            ReferenceValues.warning_low,
            ReferenceValues.target,
            ReferenceValues.warning_high,
            ReferenceValues.alarm_high,
        ],
        select(
            load_case_subquery.c.id,
            literal(reference_value.id),
            literal(reference_value.alarm_low),
            literal(reference_value.warning_low),
            literal(reference_value.target),
            literal(reference_value.warning_high),
            literal(reference_value.alarm_high),
        ),
    )

    statement = insert_statement.on_conflict_do_update(
        index_elements=[
            ReferenceValues.load_case_id,
            ReferenceValues.variable_id,
        ],
        set_={
            "alarm_low": insert_statement.excluded.alarm_low,
            "warning_low": insert_statement.excluded.warning_low,
            "target": insert_statement.excluded.target,
            "warning_high": insert_statement.excluded.warning_high,
            "alarm_high": insert_statement.excluded.alarm_high,
        },
    )

    await session.execute(statement)


async def get_variables(ids: Sequence[str]) -> list[VariableType]:
    variables: list[VariableDefinition] = [
        VARIABLES[id] for id in ids if id in VARIABLES
    ]

    if variables:
        return [
            VariableType(
                id=ID(var.id),
                name=var.name,
                unit=Unit(var.unit) if var.unit else None,
                minimum=var.minimum,
                maximum=var.maximum,
            )
            for var in variables
        ]
    else:
        logger.info(f"No variables found for ids: {ids}")
        return []


async def get_sails(ids: Sequence[str] | None, session: AsyncSession) -> list[SailType]:
    query = (
        select(SailsTable).where(SailsTable.id.in_(ids)) if ids else select(SailsTable)
    )

    result = await session.execute(query)
    sails = result.scalars().all()

    if sails:
        return [
            SailType(
                id=sail.id,  # type: ignore
                abbreviation=sail.abbreviation,  # type: ignore
                position_id=sail.position_id,  # type: ignore
                name=sail.name,  # type: ignore
                variant_name=sail.variant_name,  # type: ignore
            )
            for sail in sails
        ]
    else:
        logger.info(f"No sails found for ids: {ids}")
        return []


def create_sail_set_subq(sailset: Sequence[str]) -> ScalarSelect[int]:
    """Create subquery that returns the sail set that exactly matches the current sails."""
    return (
        select(SailSetsCombined.id)
        .where(sails_exact(SailSetsCombined.sails, sailset))
        .scalar_subquery()
    )


def sails_exact(
    sails_column: Column[Sequence[str]], sails: Sequence[str]
) -> ColumnElement[bool]:
    """Check if the sail set exactly matches the sails provided"""
    return sails_column == cast(sorted(sails), ARRAY(TEXT))


def create_load_case_subq(
    awa_ranges: list[AwaRange], aws_ranges: list[AwsRange], sailset: Sequence[str]
) -> Subquery:
    return (
        select(LoadCases.id)
        .where(LoadCases.sail_set_id == create_sail_set_subq(sailset))
        .join(AwaRanges, LoadCases.awa_range_id == AwaRanges.id)
        .join(AwsRanges, LoadCases.aws_range_id == AwsRanges.id)
        .where(
            AwaRanges.id.in_([awa_range.value for awa_range in awa_ranges]),
            or_(*[
                AwsRanges.aws_range == text(f"'{aws_range.value}'::numrange")
                for aws_range in aws_ranges
            ]),
        )
        .subquery()
    )
