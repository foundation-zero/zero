import strawberry
from .db import AsyncSessionLocal, SailSetCombined
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional
from .types import CaseInput, ReferenceValueType
import logging
from sqlalchemy import select
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import TEXT, ARRAY

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
                print(f"Input: {values}")
                print(case)
                print(f"Sails: {case.sails}, {type(case.sails[0])}")
                sail_set_subq = select(SailSetCombined.id).where(
                    SailSetCombined.sails.contains(
                        cast(
                            case.sails,
                            ARRAY(TEXT),
                        )
                    )
                )

                # condition_subq = (
                #     select(Conditions.id)
                #     .filter(Conditions.sea_state == case.sea_state.value)
                #     .filter(Conditions.awa.contains(case.awa))
                #     .filter(Conditions.aws.contains(case.aws))
                #     .filter(Conditions.pcs_mode_fwd.contains([case.pcs_mode.fwd.value]))
                #     .filter(Conditions.pcs_mode_aft.contains([case.pcs_mode.aft.value]))
                #     .subquery()
                # )

                # query = (
                #     select(ReferenceValue)
                #     .where(ReferenceValue.value_definition_id.in_(values))
                #     # .join(
                #     #     ValueDefinition,
                #     #     ReferenceValue.value_definition_id == ValueDefinition.id,
                #     # )
                #     .filter(ReferenceValue.sail_set_id == sail_set_subq.c.id)
                #     # .filter(ReferenceValue.condition_id == condition_subq.c.id)
                # )

                query = sail_set_subq

                result = await session.execute(query)
                rows = result.scalars().all()

                print(f"rows: {rows}")

                # # Convert SQLAlchemy objects to ReferenceValueType
                # return [
                #     ReferenceValueType(
                #         id=row.id,
                #         sail_set_id=row.sail_set_id,
                #         condition_id=row.condition_id,
                #         mast_id=row.mast_id,
                #         value_definition_id=row.value_definition_id,
                #         value=row.value,
                #         error_too_low=row.error_too_low,
                #         error_too_high=row.error_too_high,
                #         warning_too_low=row.warning_too_low,
                #         warning_too_high=row.warning_too_high,
                #     )
                #     for row in rows
                # ]
                return None


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
