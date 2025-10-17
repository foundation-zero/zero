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
) -> list[ReferenceValueType] | None:
    """Return all reference values that matches the currents sail and conditions."""

    if not case:
        current_case = await retrieve_current_load_case(session)

        if not current_case:
            logger.info("No case found")
            return None
        else:
            logger.info(f"Retrieved case: {current_case}")
            case = current_case

    sail_set = create_sail_set_subq(case)
    condition = create_condition_profiles_subq(case)

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
        logger.info(f"No reference values found for case: {case}")
        return []


def create_sail_set_subq(case: CaseInput) -> ScalarSelect[str]:
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


def create_condition_profiles_subq(case: CaseInput) -> ScalarSelect[str]:
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


async def retrieve_current_load_case(session: AsyncSession) -> CaseInput | None:
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
        return None
