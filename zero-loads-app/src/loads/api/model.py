import logging
from typing import Sequence

from sqlalchemy import Column, cast, select, text
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
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
from .types import (
    CaseInput,
    ReferenceValue,
    Sails,
    Unit,
    VariableType,
)

logger = logging.getLogger("api")


async def get_loads_reference_values(
    variables: list[str],
    case: CaseInput,
    session: AsyncSession,
) -> list[ReferenceValue] | None:
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


async def get_variables(
    ids: Sequence[str], session: AsyncSession
) -> list[VariableType]:
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


def create_sail_set_subq(sailset: list[Sails]) -> ScalarSelect[int]:
    """Create subquery that returns the sail set that exactly matches the current sails."""
    return (
        select(SailSetsCombined.id)
        .where(sails_exact(SailSetsCombined.sails, sailset))
        .scalar_subquery()
    )


def sails_exact(
    sails_column: Column[Sequence[str]], sails: list[Sails]
) -> ColumnElement[bool]:
    """Check if the sail set exactly matches the sails provided"""
    return sails_column == cast(sorted([sail.value for sail in sails]), ARRAY(TEXT))
