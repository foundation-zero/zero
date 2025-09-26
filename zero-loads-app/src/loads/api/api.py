import strawberry
from .model import get_reference_values
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from .types import (
    CaseInput,
    ReferenceValueType,
)
import logging
from .db import get_db_session, sessionmanager
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext
from dataclasses import dataclass

logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Function that handles startup and shutdown events (https://fastapi.tiangolo.com/advanced/events/)"""
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()


@dataclass
class MyContext(BaseContext):
    session: AsyncSession


async def get_context(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MyContext:
    return MyContext(session)


@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return "1.0.0"

    @strawberry.field
    async def reference_values(
        self,
        info: strawberry.Info[MyContext],
        values: list[strawberry.ID],
        case: CaseInput | None = None,
    ) -> list[ReferenceValueType]:
        return await get_reference_values(values, case, info.context.session)


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema, context_getter=get_context)


app = FastAPI(lifespan=lifespan)

app.include_router(graphql_app, prefix="/graphql")
