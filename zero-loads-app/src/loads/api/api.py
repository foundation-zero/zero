import logging
import sys
from asyncio import Task, create_task
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated

import strawberry
from aiomqtt import Client as MqttClient
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext, GraphQLRouter

from loads.config import settings
from loads.sensors import sail_systems

from .db import SessionManager
from .messaging import Messaging
from .model import get_loads_reference_values
from .types import CaseInput, ReferenceValueType, Sails

logger = logging.getLogger("api")

sessionmanager = SessionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Function that handles startup and shutdown events (https://fastapi.tiangolo.com/advanced/events/)"""
    sessionmanager.initialize(settings.pg_url)
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt:
        messaging = Messaging(
            mqtt_client=mqtt,
            modules=[sail_systems],
        )
        run_task = create_task(await messaging.run())

        def _finish(task: Task):
            if err := task.exception():
                logger.critical("Messaging failed", exc_info=err)
                sys.exit(1)

        run_task.add_done_callback(_finish)
        app.state.messaging = messaging

        yield
        run_task.cancel()
        if sessionmanager._engine is not None:
            await sessionmanager.close()


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session


def messaging() -> Messaging:
    return app.state.messaging


@dataclass
class LoadsContext(BaseContext):
    messaging: Messaging
    session: AsyncSession


async def get_context(
    messaging: Annotated[Messaging, Depends(messaging)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoadsContext:
    return LoadsContext(messaging=messaging, session=session)


@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return "1.0.0"

    @strawberry.field
    async def reference_values(
        self,
        info: strawberry.Info[LoadsContext],
        values: list[strawberry.ID],
        sails: list[Sails],
        case: CaseInput | None = None,
    ) -> list[ReferenceValueType] | None:
        return await get_loads_reference_values(values=values, sails=sails, case=case, session=info.context.session)


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema, context_getter=get_context)


app = FastAPI(lifespan=lifespan)


app.include_router(graphql_app, prefix="/graphql")
