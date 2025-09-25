import strawberry
from .model import get_reference_values
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from .types import (
    CaseInput,
    ReferenceValueType,
)
import logging

logger = logging.getLogger("api")


@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return "1.0.0"

    @strawberry.field
    async def reference_values(
        self,
        values: list[strawberry.ID],
        case: CaseInput | None = None,
    ) -> list[ReferenceValueType]:
        return await get_reference_values(values, case)


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
