import strawberry
from .db import (
    AsyncSessionLocal,
    SailSetCombined,
    Conditions,
    ReferenceValue,
    ValueDefinition,
)
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional
from .types import CaseInput, ReferenceValueType, ValueType, RangesType, Unit
import logging
from sqlalchemy import select
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import TEXT, ARRAY, NUMERIC

logger = logging.getLogger("api")


@strawberry.type
class Query:
    @strawberry.field
    async def reference_values(
        self,
        values: List[strawberry.ID],
        case: Optional[CaseInput] = None,
    ) -> List[ReferenceValueType]:
        async with AsyncSessionLocal() as session:
            if case:
                sail_set_subq = (
                    select(SailSetCombined.id)
                    .where(SailSetCombined.sails == cast(case.sails, ARRAY(TEXT)))
                    .scalar_subquery()
                )

                condition_subq = (
                    select(Conditions.id)
                    .where(Conditions.sea_state == case.sea_state)
                    .where(Conditions.awa.contains(cast(case.awa, NUMERIC)))
                    .where(Conditions.aws.contains(cast(case.aws, NUMERIC)))
                    .where(Conditions.pcs_mode_fwd.any(case.pcs_mode.fwd.value))
                    .where(Conditions.pcs_mode_aft.any(case.pcs_mode.aft.value))
                    .scalar_subquery()
                )

                query = (
                    select(ReferenceValue, ValueDefinition)
                    .join(
                        ValueDefinition,
                        ReferenceValue.value_definition_id == ValueDefinition.id,
                    )
                    .where(ReferenceValue.value_definition_id.in_(values))
                    .where(ReferenceValue.sail_set_id.in_(sail_set_subq))
                    .where(ReferenceValue.condition_id.in_(condition_subq))
                )

                result = await session.execute(query)
                rows = result.fetchall()

                print(f"row: {rows}")
                return [
                    ReferenceValueType(
                        value=ValueType(
                            id=row[1].id,
                            name=row[1].name,
                        ),
                        target=row[0].value,
                        ranges=RangesType(
                            error_too_low=row[0].error_too_low,
                            warning_too_low=row[0].warning_too_low,
                            warning_too_high=row[0].warning_too_high,
                            error_too_high=row[0].error_too_high,
                        ),
                        unit=Unit(row[1].unit),
                    )
                    for row in rows
                ]
            return []


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
