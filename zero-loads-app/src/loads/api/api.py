import logging
import sys
from asyncio import Task, create_task
from contextlib import asynccontextmanager
from dataclasses import dataclass
from itertools import groupby
from typing import Annotated, Sequence

import strawberry
from aiomqtt import Client as MqttClient
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext, GraphQLRouter

from loads.config import settings
from loads.registry import VARIABLES, at_sensors, sail_system_sensors

from .db import SessionManager
from .messaging import Messaging
from .model import (
    get_loads_reference_values,
    set_loads_reference_values,
)
from .model import (
    get_variables as db_get_variables,
)
from .types import (
    ActualType,
    AwaRange,
    AwsRange,
    CaseInput,
    ReferenceValue,
    ReferenceValueInput,
    Sails,
    VariableType,
)

logger = logging.getLogger("api")

sessionmanager = SessionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Function that handles startup and shutdown events (https://fastapi.tiangolo.com/advanced/events/)"""
    sessionmanager.initialize(settings.pg_url)
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt:
        messaging = Messaging(
            mqtt_client=mqtt,
            modules=[sail_system_sensors, at_sensors],
            variable_definitions=VARIABLES,
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
    sessionmanager: SessionManager
    actuals_loader: DataLoader[str, ActualType]
    references_loader: DataLoader[
        tuple[strawberry.ID, CaseInput], ReferenceValue | None
    ]
    variables_loader: DataLoader[str, VariableType | None]


async def get_actuals(
    variables: Sequence[str], context: LoadsContext
) -> list[ActualType | None]:
    values = context.messaging.get_values_for(list(variables))
    result: list[ActualType | None] = [None] * len(variables)
    for value in values:
        index = variables.index(value.id)
        result[index] = value
    return result


async def get_reference_values(
    keys: list[tuple[strawberry.ID, CaseInput]], context: LoadsContext
) -> list[ReferenceValue | None]:
    async with context.sessionmanager.session() as session:
        by_case = groupby(keys, lambda x: x[1])
        results: list[ReferenceValue | None] = [None] * len(keys)
        for case, group in by_case:
            variables = [str(var_id) for var_id, _ in group]
            values = (
                await get_loads_reference_values(
                    variables=variables,
                    case=case,
                    session=session,
                )
                or []
            )
            for value in values:
                results[keys.index((value.id, case))] = value

    return results


async def get_variables(
    ids: Sequence[str], context: LoadsContext
) -> list[VariableType | None]:
    async with context.sessionmanager.session() as session:
        variables = await db_get_variables(ids, session)
        result: list[None | VariableType] = [None] * len(ids)
        for var in variables:
            index = ids.index(var.id)
            result[index] = var

    return result


async def get_context(
    messaging: Annotated[Messaging, Depends(get_messaging)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoadsContext:
    context = LoadsContext(
        messaging=messaging,
        sessionmanager=sessionmanager,
        actuals_loader=DataLoader(
            load_fn=lambda keys: get_actuals(keys, context),  # type: ignore
            cache=False,
        ),
        references_loader=DataLoader(
            load_fn=lambda keys: get_reference_values(keys, context),  # type: ignore
            cache=False,
        ),
        variables_loader=DataLoader(
            load_fn=lambda keys: get_variables(keys, context),  # type: ignore
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
    async def variable(
        self, info: strawberry.Info[LoadsContext]
    ) -> VariableType | None:
        return await info.context.variables_loader.load(self.id)

    @strawberry.field
    async def reference(
        self,
        info: strawberry.Info[LoadsContext],
        case: CaseInput,
    ) -> ReferenceValue | None:
        return await info.context.references_loader.load((self.id, case))


@strawberry.type
class Query:
    @strawberry.field
    async def variables(
        self,
        variables: list[strawberry.ID] | None = None,
    ) -> list[Variable]:
        if variables is None:
            variables = [strawberry.ID(var_id) for var_id in VARIABLES.keys()]
        return [Variable(id=var_id) for var_id in variables]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def set_reference_values(
        self,
        info: strawberry.Info[LoadsContext],
        reference_value: ReferenceValueInput,
        sail_set: list[Sails],
        awa_ranges: list[AwaRange],
        aws_ranges: list[AwsRange],
    ) -> None:
        async with info.context.sessionmanager.session() as session:
            await set_loads_reference_values(
                reference_value, sail_set, awa_ranges, aws_ranges, session
            )


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)


app = FastAPI(lifespan=lifespan)


app.include_router(graphql_app, prefix="/graphql")
