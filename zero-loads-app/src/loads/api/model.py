import strawberry
from sqlalchemy import select, cast, Column
from sqlalchemy.sql.selectable import ScalarSelect
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.dialects.postgresql import ARRAY, NUMERIC, TEXT
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from .schema import (
    Conditions,
    Masts,
    ReferenceValues,
    SailSetCombined,
    ValueDefinitions,
)
from .types import (
    AlertType,
    CaseInput,
    MastType,
    ReferenceValueType,
    TargetType,
    Unit,
    ValueType,
)


async def get_reference_values(
    values: list[strawberry.ID], case: CaseInput | None, session: AsyncSession
):
    """Return all reference values that matches the currents sail and conditions."""
    if case:
        sail_set = retrieve_sail_set_subq(case)
        condition = retrieve_conditions_subq(case)
    else:
        # TODO: ZERO-709: Get these values from the control process
        sail_set = "upwind-blade"
        condition = "light-wind-close-hauled"

    query = (
        select(ReferenceValues, ValueDefinitions, Masts)
        .join(
            ValueDefinitions,
            ReferenceValues.value_definition_id == ValueDefinitions.id,
        )
        .join(Masts, ReferenceValues.mast_id == Masts.id)
        .where(ReferenceValues.value_definition_id.in_(values))
        .where(ReferenceValues.sail_set_id == sail_set)
        .where(ReferenceValues.condition_id == condition)
    )

    result = await session.execute(query)
    rows = result.fetchall()

    return [
        ReferenceValueType(
            value=ValueType(
                id=definition.id,
                name=definition.name,
            ),
            masts=MastType(id=mast.id, name=mast.name),
            target=TargetType(target=reference.value, unit=Unit(definition.unit)),
            ranges=AlertType(
                error_too_low=reference.error_too_low,
                warning_too_low=reference.warning_too_low,
                warning_too_high=reference.warning_too_high,
                error_too_high=reference.error_too_high,
            ),
        )
        for reference, definition, mast in rows
    ]


def retrieve_sail_set_subq(case: CaseInput) -> ScalarSelect[str]:
    """Retrieve subquery that returns the sail set that exactly matches the current sails."""
    sail_set_subq = (
        select(SailSetCombined.id)
        .where(sails_exact(SailSetCombined.sails, case.sails))
        .scalar_subquery()
    )

    return sail_set_subq


def sails_exact(
    sails_column: Column[Sequence[str]], sails: list[str]
) -> ColumnElement[bool]:
    """Check if the sail set exactly matches the sails provided"""
    return sails_column == cast(sorted(sails), ARRAY(TEXT))


def retrieve_conditions_subq(case: CaseInput) -> ScalarSelect[str]:
    """Retrieve subquery that returns the conditions matching the case input."""
    condition_subq = (
        select(Conditions.id)
        .where(Conditions.sea_state == case.sea_state.value)
        .where(Conditions.awa.contains(cast(case.awa, NUMERIC)))
        .where(Conditions.aws.contains(cast(case.aws, NUMERIC)))
        .where(Conditions.pcs_mode_fwd.any(case.pcs_mode.fwd.value))
        .where(Conditions.pcs_mode_aft.any(case.pcs_mode.aft.value))
        .scalar_subquery()
    )

    return condition_subq
