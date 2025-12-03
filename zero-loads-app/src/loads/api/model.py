import logging

import strawberry
from sqlalchemy import cast, select
from sqlalchemy.dialects.postgresql import ARRAY, NUMERIC, TEXT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .schema import (
    AwaRanges,
    AwsRanges,
    LoadCases,
    ReferenceValues,
    SailSets,
)
from .types import (
    CaseInput,
    ReferenceValue,
    ReferenceValueType,
    Unit,
    VariableType,
)

logger = logging.getLogger("api")


async def get_loads_reference_values(
    variables: list[strawberry.ID],
    case: CaseInput,
    session: AsyncSession,
) -> list[ReferenceValueType] | None:
    """Return all reference values that match the current sails and conditions."""

    query = (
        select(ReferenceValues)
        .options(selectinload(ReferenceValues.variable))
        .where(ReferenceValues.variable_id.in_(variables))
        .where(
            ReferenceValues.load_case.has(
                LoadCases.awa_range.has(AwaRanges.awa.contains(cast(case.awa, NUMERIC)))
            )
        )
        .where(
            ReferenceValues.load_case.has(
                LoadCases.aws_range.has(AwsRanges.aws.contains(cast(case.aws, NUMERIC)))
            )
        )
        .where(
            ReferenceValues.load_case.has(
                LoadCases.sail_set.has(
                    SailSets.sail_set.contains(
                        cast([sail.value for sail in case.sailset], ARRAY(TEXT))
                    )
                )
            )
        )
        .where(
            ReferenceValues.load_case.has(
                LoadCases.sail_set.has(
                    SailSets.sail_set.contained_by(
                        cast([sail.value for sail in case.sailset], ARRAY(TEXT))
                    )
                )
            )
        )
    )

    result = await session.execute(query)
    reference_values = result.scalars().all()

    if reference_values:
        return [
            ReferenceValueType(
                variable=VariableType(
                    id=ref_value.variable.id,
                    name=ref_value.variable.name,
                    unit=Unit(ref_value.variable.unit),
                ),
                reference=ReferenceValue(
                    alarm_low=ref_value.alarm_low,  # type: ignore
                    warning_low=ref_value.warning_low,  # type: ignore
                    target=ref_value.target,  # type: ignore
                    warning_high=ref_value.warning_high,  # type: ignore
                    alarm_high=ref_value.alarm_high,  # type: ignore
                ),
            )
            for ref_value in reference_values
        ]
    else:
        logger.info(f"No reference values found for case: {case}")
        return []
