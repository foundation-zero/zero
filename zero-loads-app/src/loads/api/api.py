import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated

import strawberry
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext, GraphQLRouter

from loads.config import settings

from .db import SessionManager
from .model import get_loads_reference_values
from .types import CaseInput, ReferenceValueType

logger = logging.getLogger("api")

sessionmanager = SessionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Function that handles startup and shutdown events (https://fastapi.tiangolo.com/advanced/events/)"""
    sessionmanager.initialize(settings.pg_url)
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session


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
    ) -> list[ReferenceValueType] | None:
        return await get_loads_reference_values(values, case, info.context.session)


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema, context_getter=get_context)


app = FastAPI(lifespan=lifespan)

app.include_router(graphql_app, prefix="/graphql")
