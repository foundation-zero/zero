import logging
from typing import Sequence

import strawberry
from sqlalchemy import Column, cast, select
from sqlalchemy.dialects.postgresql import ARRAY, NUMERIC, TEXT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.sql.selectable import ScalarSelect

from .schema import (
    Conditions,
    ConditionsProfiles,
    Masts,
    ReferenceValues,
    SailSetCombined,
    ValueDefinitions,
)
from .types import (
    AlertType,
    CaseInput,
    MastType,
    PCSModeInput,
    ReferenceValueType,
    SeaState,
    TargetType,
    ThrusterMode,
    Unit,
    ValueType,
)

logger = logging.getLogger("api")


async def get_loads_reference_values(
    values: list[strawberry.ID], case: CaseInput | None, session: AsyncSession
) -> list[ReferenceValueType]:
    """Return all reference values that matches the currents sail and conditions."""

    if not case:
        case = await retrieve_current_load_case(session)
        logger.info(f"Retrieved case: {case}")

    sail_set = retrieve_sail_set_subq(case)
    condition = retrieve_conditions_profiles_subq(case)

    query = (
        select(ReferenceValues, ValueDefinitions, Masts)
        .join(
            ValueDefinitions,
            ReferenceValues.value_definition_id == ValueDefinitions.id,
        )
        .join(Masts, ReferenceValues.mast_id == Masts.id)
        .where(ReferenceValues.value_definition_id.in_(values))
        .where(ReferenceValues.sail_set_id == sail_set)
        .where(ReferenceValues.condition_profile_id == condition)
    )

    result = await session.execute(query)
    rows = result.fetchall()

    if rows:
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
    else:
        raise ValueError(f"No reference values found for case {case}.")


def retrieve_sail_set_subq(case: CaseInput) -> ScalarSelect[str]:
    """Create subquery that returns the sail set that exactly matches the current sails."""
    return (
        select(SailSetCombined.id)
        .where(sails_exact(SailSetCombined.sails, case.sails))
        .scalar_subquery()
    )


def sails_exact(
    sails_column: Column[Sequence[str]], sails: list[str]
) -> ColumnElement[bool]:
    """Check if the sail set exactly matches the sails provided"""
    return sails_column == cast(sorted(sails), ARRAY(TEXT))


def retrieve_conditions_profiles_subq(case: CaseInput) -> ScalarSelect[str]:
    """Create subquery that returns the condition profile matching the input conditions."""
    return (
        select(ConditionsProfiles.id)
        .where(ConditionsProfiles.sea_state == case.sea_state)
        .where(ConditionsProfiles.awa.contains(cast(case.awa, NUMERIC)))
        .where(ConditionsProfiles.aws.contains(cast(case.aws, NUMERIC)))
        .where(ConditionsProfiles.pcs_mode_fwd.any(case.pcs_mode.fwd))
        .where(ConditionsProfiles.pcs_mode_aft.any(case.pcs_mode.aft))
        .scalar_subquery()
    )


async def retrieve_current_load_case(session: AsyncSession) -> CaseInput:
    """Retrieve the most recent load case from the database."""
    load_case_current = select(Conditions).order_by(Conditions.time.desc()).limit(1)
    result = await session.execute(load_case_current)
    row = result.scalar_one_or_none()
    if row:
        return CaseInput(
            sails=list(row.sails),  # type: ignore
            sea_state=SeaState(row.sea_state),
            pcs_mode=PCSModeInput(
                fwd=ThrusterMode(row.pcs_mode_fwd),
                aft=ThrusterMode(row.pcs_mode_aft),
            ),
            awa=float(row.awa),  # type: ignore
            aws=float(row.aws),  # type: ignore
        )
    else:
        raise ValueError("No load case found.")
