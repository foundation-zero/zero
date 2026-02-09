import logging
import sys
from asyncio import Task, create_task
from contextlib import asynccontextmanager
from itertools import groupby
from typing import Annotated, Sequence

import strawberry
from aiomqtt import Client as MqttClient
from fastapi import Depends, FastAPI
from strawberry.dataloader import DataLoader
from strawberry.fastapi import GraphQLRouter

from loads.config import settings
from loads.registry import ALARMS, VARIABLES, at_sensors, sail_system_sensors

from .db import SessionManager
from .messaging import Messaging
from .model import (
    get_alarms as model_get_alarms,
)
from .model import (
    get_loads_reference_values,
    get_sails,
    set_loads_reference_values,
)
from .model import (
    get_variables as model_get_variables,
)
from .types import (
    AlarmType,
    AwaRange,
    AwsRange,
    CaseInput,
    LoadsContext,
    ReferenceValue,
    ReferenceValueInput,
    SailType,
    Variable,
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
            alarm_definitions=ALARMS,
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


async def get_reference_values(
    keys: list[tuple[strawberry.ID, CaseInput]], context: LoadsContext
) -> list[ReferenceValue | None]:
    async with context.sessionmanager.session() as session:
        by_case = groupby(keys, lambda x: x[1])
        by_id_case = {}
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
                by_id_case[(value.id, case)] = value

    return [by_id_case.get((var_id, case)) for var_id, case in keys]


async def get_variables(
    ids: Sequence[str], context: LoadsContext
) -> list[VariableType | None]:
    variables = await model_get_variables(ids)
    vars_by_id = {str(var.id): var for var in variables}
    result: list[None | VariableType] = [vars_by_id.get(var_id) for var_id in ids]

    return result


async def get_context(
    messaging: Annotated[Messaging, Depends(get_messaging)],
) -> LoadsContext:
    context = LoadsContext(
        messaging=messaging,
        sessionmanager=sessionmanager,
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
class Query:
    @strawberry.field
    async def variables(
        self,
        variables: list[strawberry.ID] | None = None,
    ) -> list[Variable]:
        if variables is None:
            variables = [strawberry.ID(var_id) for var_id in VARIABLES.keys()]
        return [Variable(id=var_id) for var_id in variables]

    @strawberry.field
    async def sails(
        self,
        info: strawberry.Info[LoadsContext],
        sails: list[strawberry.ID] | None = None,
    ) -> list[SailType]:
        async with info.context.sessionmanager.session() as session:
            return await get_sails(sails, session)

    @strawberry.field
    async def alarms(
        self,
        info: strawberry.Info[LoadsContext],
        alarms: list[strawberry.ID] | None = None,
        active: Annotated[
            bool | None, strawberry.argument(description="Filter by active state")
        ] = None,
    ) -> list[AlarmType]:
        if alarms is None:
            alarms = [strawberry.ID(alarm_id) for alarm_id in ALARMS.keys()]
        valid_alarms = model_get_alarms([str(alarm_id) for alarm_id in alarms])
        if active is not None:
            return [alarm for alarm in valid_alarms if alarm.active(info) == active]  # type: ignore[arg-type]
        return valid_alarms


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def set_reference_values(
        self,
        info: strawberry.Info[LoadsContext],
        reference_value: ReferenceValueInput,
        sail_set: list[strawberry.ID],
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
