import strawberry
from typing import Sequence
from sqlalchemy.future import select
from .db import AsyncSessionLocal
from .db import ReferenceValue
import uvicorn
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class ReferenceValueType:
    id: int
    sail_set_id: str
    condition_id: str
    mast_id: int
    value_definition_id: str
    value: float
    error_too_low: bool
    error_too_high: bool
    warning_too_low: bool
    warning_too_high: bool


async def get_reference_values() -> Sequence[ReferenceValueType]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ReferenceValue))
        return result.scalars().all()


@strawberry.type
class Query:
    @strawberry.field
    async def reference_values(
        self, sail_set_id: str = None, condition_id: str = None, mast_id: int = None
    ) -> Sequence[ReferenceValueType]:
        async with AsyncSessionLocal() as session:
            query = select(ReferenceValue)
            if sail_set_id:
                query = query.filter(ReferenceValue.sail_set_id == sail_set_id)
            if condition_id:
                query = query.filter(ReferenceValue.condition_id == condition_id)
            if mast_id:
                query = query.filter(ReferenceValue.mast_id == mast_id)
            result = await session.execute(query)
            return result.scalars().all()


schema = strawberry.Schema(query=Query)

graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
