import logging
from collections import defaultdict
from typing import Literal, Sequence

from sqlalchemy import Column, Subquery, cast, literal, or_, select, text
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.sql.selectable import ScalarSelect
from strawberry import ID

from loads.registry import ALARMS, VARIABLES, AlarmDefinition, VariableDefinition
from loads.registry.registry import Applicability

from .schema import (
    AwaRanges,
    AwsRanges,
    LoadCaseMappings,
    LoadCases,
    ReferenceValues,
    SailSets,
    SailSetsCombined,
)
from .schema import (
    Sails as SailsTable,
)
from .types import (
    AlarmType,
    AwaRange,
    AwsRange,
    CaseInput,
    LoadCase,
    ReferenceValue,
    ReferenceValueInput,
    SailType,
    Unit,
    VariableType,
)

logger = logging.getLogger("api")


async def get_loads_reference_values(
    variable_keys: list[str],
    case: CaseInput,
    session: AsyncSession,
) -> list[ReferenceValue]:
    """Return all reference values that match the current sails and conditions."""

    mapping_lookup = create_load_case_mapping_subq(case)

    query = select(ReferenceValues).where(
        ReferenceValues.variable_key.in_(variable_keys),
        ReferenceValues.load_case_id == mapping_lookup.scalar_subquery(),
    )

    result = await session.execute(query)
    reference_values = result.scalars().all()

    if reference_values:
        return [
            ReferenceValue(
                id=ref_value.variable_key,  # type: ignore
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


async def get_load_case(
    case: CaseInput,
    session: AsyncSession,
) -> LoadCase | None:
    """Return the load case that matches the current sails and conditions."""

    mapping_lookup = create_load_case_mapping_subq(case)

    query = select(LoadCases).where(LoadCases.id == mapping_lookup.scalar_subquery())

    result = await session.execute(query)
    load_case = result.scalar_one_or_none()

    if load_case is None:
        return None

    return LoadCase(
        id=ID(str(load_case.id)),
        name=load_case.name,  # type: ignore
        awa=load_case.awa,  # type: ignore
        aws=load_case.aws,  # type: ignore
    )


async def get_load_cases(session: AsyncSession) -> list[LoadCase]:
    """Return all load cases."""

    result = await session.execute(select(LoadCases))
    load_cases = result.scalars().all()

    return [
        LoadCase(
            id=ID(str(load_case.id)),
            name=load_case.name,  # type: ignore
            awa=load_case.awa,  # type: ignore
            aws=load_case.aws,  # type: ignore
        )
        for load_case in load_cases
    ]


async def get_reference_values_by_case_ids(
    load_case_ids: Sequence[str], session: AsyncSession
) -> dict[str, list[ReferenceValue]]:
    """Return all reference values grouped by load-case id."""

    if not load_case_ids:
        return {}

    load_case_id_col = cast(ReferenceValues.load_case_id, TEXT)
    query = select(load_case_id_col.label("load_case_id"), ReferenceValues).where(
        load_case_id_col.in_([str(load_case_id) for load_case_id in load_case_ids])
    )

    result = await session.execute(query)
    grouped: dict[str, list[ReferenceValue]] = defaultdict(list)

    for load_case_id, ref_value in result.all():
        grouped[str(load_case_id)].append(
            ReferenceValue(
                id=ref_value.variable_key,  # type: ignore
                alarm_low=ref_value.alarm_low,  # type: ignore
                warning_low=ref_value.warning_low,  # type: ignore
                target=ref_value.target,  # type: ignore
                warning_high=ref_value.warning_high,  # type: ignore
                alarm_high=ref_value.alarm_high,  # type: ignore
            )
        )

    return grouped


async def get_sails_by_case_ids(
    load_case_ids: Sequence[str], session: AsyncSession
) -> dict[str, list[SailType]]:
    """Return all sails grouped by load-case id."""

    if not load_case_ids:
        return {}

    load_case_id_col = cast(LoadCases.id, TEXT)
    query = (
        select(load_case_id_col.label("load_case_id"), SailsTable)
        .join(SailSets, SailSets.sail_set_id == LoadCases.sail_set_id)
        .join(SailsTable, SailsTable.id == SailSets.sail_id)
        .where(
            load_case_id_col.in_([str(load_case_id) for load_case_id in load_case_ids])
        )
    )

    result = await session.execute(query)
    grouped: dict[str, list[SailType]] = defaultdict(list)

    for load_case_id, sail in result.all():
        grouped[str(load_case_id)].append(
            SailType(
                id=sail.id,  # type: ignore
                abbreviation=sail.abbreviation,  # type: ignore
                position_id=sail.position_id,  # type: ignore
                name=sail.name,  # type: ignore
                variant_name=sail.variant_name,  # type: ignore
            )
        )

    return grouped


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
            ReferenceValues.variable_key,
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
            ReferenceValues.variable_key,
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


def resolve_variable_definitions(ids: Sequence[str]) -> list[VariableDefinition]:
    return [VARIABLES[id] for id in ids if id in VARIABLES]


def get_variables(ids: Sequence[str]) -> list[VariableType]:
    if variables := resolve_variable_definitions(ids):
        return [
            VariableType(
                id=ID(var.id),
                name=var.name,
                unit=Unit(var.unit) if var.unit else None,
                scale_min=var.scale_min,
                scale_max=var.scale_max,
                scale_min_label=var.scale_min_label,
                scale_max_label=var.scale_max_label,
            )
            for var in variables
        ]
    else:
        logger.info(f"No variables found for ids: {ids}")
        return []


def resolve_variable_keys(
    variables: Sequence[VariableDefinition],
    tack: Literal["port", "starboard"],
) -> list[str]:
    def _apply_applicability(variable: VariableDefinition):
        match variable.applicability:
            case None:
                return variable.id
            case Applicability(key, applies_to_tack) if applies_to_tack == tack:
                return key
            case _:
                return None

    return [key for var in variables if (key := _apply_applicability(var))]


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


def get_alarms(ids: Sequence[str]) -> list[AlarmType]:
    alarms: list[AlarmDefinition] = [ALARMS[id] for id in ids if id in ALARMS]

    if alarms:
        return [
            AlarmType(
                id=alarm.id,
                name=alarm.name,
                actual_variable_id=ID(alarm.actual_definition.id),
            )
            for alarm in alarms
        ]
    else:
        logger.info(f"No alarms found for ids: {ids}")
        return []


def create_sail_set_subq(sailset: Sequence[str]) -> ScalarSelect[int]:
    """Create subquery that returns the sail set that exactly matches the current sails."""
    return (
        select(SailSetsCombined.id)
        .where(sails_exact(SailSetsCombined.sails, sailset))
        .scalar_subquery()
    )


def create_load_case_mapping_subq(case: CaseInput):
    """Create query for a load-case mapping matching current ranges and sail set."""
    return (
        select(LoadCaseMappings.load_case_id)
        .join(AwsRanges, AwsRanges.id == LoadCaseMappings.aws_range_id)
        .where(
            LoadCaseMappings.awa_range_id == case.awa_range.value,
            AwsRanges.aws_range == text(f"'{case.aws_range.value}'::numrange"),
            LoadCaseMappings.sail_set_id == create_sail_set_subq(case.sailset),
        )
        .limit(1)
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
        .join(LoadCaseMappings, LoadCaseMappings.load_case_id == LoadCases.id)
        .join(AwaRanges, AwaRanges.id == LoadCaseMappings.awa_range_id)
        .join(AwsRanges, AwsRanges.id == LoadCaseMappings.aws_range_id)
        .where(
            LoadCaseMappings.sail_set_id == create_sail_set_subq(sailset),
            AwaRanges.id.in_([awa_range.value for awa_range in awa_ranges]),
            or_(
                *[
                    AwsRanges.aws_range == text(f"'{aws_range.value}'::numrange")
                    for aws_range in aws_ranges
                ]
            ),
        )
        .subquery()
    )
