import logging
import sys
from asyncio import Task, create_task
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated, Sequence

import strawberry
from aiomqtt import Client as MqttClient
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext, GraphQLRouter

from loads.config import settings
from loads.sensors import sail_systems

from .db import SessionManager
from .loads import loads_variables
from .messaging import Messaging
from .model import get_loads_reference_values
from .types import ActualType, CaseInput, ReferenceValueType

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
            variable_definition=loads_variables,
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


def get_messaging() -> Messaging:
    return app.state.messaging


@dataclass
class LoadsContext(BaseContext):
    messaging: Messaging
    session: AsyncSession
    actuals_loader: DataLoader
    references_loader: DataLoader


async def get_actuals(variables: Sequence[str], context: LoadsContext) -> list[ActualType]:
    return context.messaging.get_values_for(list(variables))


async def get_reference_values(
    keys: list[tuple[str, CaseInput]], context: LoadsContext
) -> list[ReferenceValueType | None]:
    results = []
    for variable, case in keys:
        ref = await get_loads_reference_values(
            variables=[variable],
            case=case,
            session=context.session,
        )
        results.append(ref[0] if ref else None)

    return results


async def get_context(
    messaging: Annotated[Messaging, Depends(get_messaging)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoadsContext:
    context = LoadsContext(
        messaging=messaging,
        session=session,
        actuals_loader=DataLoader(
            load_fn=lambda keys: get_actuals(keys, context),  # type: ignore
            cache=False,
        ),
        references_loader=DataLoader(
            load_fn=lambda keys: get_reference_values(keys, context),  # type: ignore
            cache=False,
        ),
    )

    return context


@strawberry.type
class Variable:
    id: strawberry.ID

    @strawberry.field
    async def actual(self, info: strawberry.Info[LoadsContext]) -> ActualType | None:
        return await info.context.actuals_loader.load(self.id)

    @strawberry.field
    async def reference(
        self,
        info: strawberry.Info[LoadsContext],
        case: CaseInput,
    ) -> ReferenceValueType | None:
        return await info.context.references_loader.load((self.id, case))


@strawberry.type
class Query:
    @strawberry.field
    async def variables(
        self,
        info: strawberry.Info[LoadsContext],
        variables: list[strawberry.ID],
    ) -> list[Variable]:
        return [Variable(id=var_id) for var_id in variables]


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema, context_getter=get_context)


app = FastAPI(lifespan=lifespan)


app.include_router(graphql_app, prefix="/graphql")
