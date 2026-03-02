import logging
from typing import Annotated

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from loads.api.dependencies import get_context, lifespan
from loads.registry import (
    ALARMS,
    VARIABLES,
)

from .health import router as health_router
from .model import (
    get_alarms as model_get_alarms,
)
from .model import (
    get_sails,
    set_loads_reference_values,
)
from .types import (
    AlarmType,
    AwaRange,
    AwsRange,
    LoadsContext,
    ReferenceValueInput,
    SailType,
    Variable,
)

logger = logging.getLogger("api")


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
app.include_router(health_router, prefix="/health")
