from .db import (
    AsyncSessionLocal,
    SailSetCombined,
    Conditions,
    ReferenceValues,
    ValueDefinitions,
    Masts,
)
from sqlalchemy import select, cast
from sqlalchemy.dialects.postgresql import TEXT, ARRAY, NUMERIC
from .types import (
    ReferenceValueType,
    ValueType,
    TargetType,
    Unit,
    MastType,
    AlertType,
)
from .types import CaseInput


async def get_reference_values(values, case):
    """Retrieve reference values based on sail set and conditions."""
    async with AsyncSessionLocal() as session:
        if case:
            sail_set = retrieve_sail_set_subq(case)
            condition = retrieve_conditions_subq(case)
        else:
            # TODO: ZERO-709: Get these values from the control process
            sail_set = "upwind-blade"  # type: ignore
            condition = "light-wind-close-hauled"  # type: ignore

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


def retrieve_sail_set_subq(case: CaseInput):
    """Retrieve sail set based on current sails."""
    sail_set_subq = (
        select(SailSetCombined.id)
        .where(SailSetCombined.sails == cast(sorted(case.sails), ARRAY(TEXT)))
        .scalar_subquery()
    )

    return sail_set_subq


def retrieve_conditions_subq(case: CaseInput):
    """Retrieve conditions based on case input."""
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
