import strawberry
from sqlalchemy.future import select
from .db import AsyncSessionLocal, ReferenceValue, SailSet, Conditions
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional
from .types import ReferenceValueType, CaseInput


@strawberry.type
class Query:
    @strawberry.field
    async def reference_values(
        self,
        values: List[strawberry.ID],
        case: Optional[CaseInput] = None,
    ) -> List[ReferenceValueType]:
        async with AsyncSessionLocal() as session:
            query = select(ReferenceValue).where(
                ReferenceValue.value_definition_id.in_(values)
            )
            if case:
                sail_set_subq = query.where(SailSet.sails.contains(case.sails))

                condition_subq = (
                    query.where(Conditions.sea_state == case.sea_state.value)
                    .where(Conditions.awa.contains(case.awa))
                    .where(Conditions.aws.contains(case.aws))
                )

                # query = query.where(ReferenceValue.sail_set_id == sail_set_id).where(
                #     ReferenceValue.condition_id == case.sea_state.value
                # )

            result = await session.execute(query)
            rows = result.scalars().all()

            return rows


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
