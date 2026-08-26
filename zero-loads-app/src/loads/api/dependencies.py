import logging
import sys
from asyncio import Task, create_task
from collections.abc import Sequence
from contextlib import asynccontextmanager
from itertools import groupby

import strawberry
from aiomqtt import Client as MqttClient
from fastapi import Depends, FastAPI, Request
from strawberry.dataloader import DataLoader
from typing_extensions import Annotated

from loads.config import settings
from loads.registry import (
    ALARMS,
    VARIABLES,
    at_sensors,
    fiber_optic_sensors,
    sail_system_sensors,
)

from .db import SessionManager
from .messaging import Messaging
from .model import (
    get_loads_reference_values,
    get_reference_values_by_case_ids,
    get_sails_by_case_ids,
    resolve_variable_definitions,
    resolve_variable_keys,
)
from .model import (
    get_variables as model_get_variables,
)
from .types import (
    CaseInput,
    LoadsContext,
    ReferenceValue,
    SailType,
    VariableType,
)

logger = logging.getLogger("api")
sessionmanager = SessionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Function that handles startup and shutdown events (https://fastapi.tiangolo.com/advanced/events/)"""
    sessionmanager.initialize(settings.pg_url)
    async with MqttClient(
        settings.mqtt_host,
        settings.mqtt_port,
        username=settings.mqtt_username,
        password=settings.mqtt_password,
    ) as mqtt:
        messaging = Messaging(
            mqtt_client=mqtt,
            modules=[sail_system_sensors, at_sensors, fiber_optic_sensors],
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


def get_messaging(request: Request) -> Messaging:
    return request.app.state.messaging


def get_sessionmanager() -> SessionManager:
    return sessionmanager


async def get_reference_values(
    keys: list[tuple[strawberry.ID, CaseInput]], context: LoadsContext
) -> list[ReferenceValue | None]:
    async with context.sessionmanager.session() as session:
        by_case = groupby(keys, lambda x: x[1])
        by_id_case = {}
        for case, group in by_case:
            variable_ids = [str(var_id) for var_id, _ in group]
            variables = resolve_variable_definitions(variable_ids)
            variable_keys = resolve_variable_keys(variables, case.tack.value)
            key_to_id = dict(zip(variable_keys, variable_ids))
            values = (
                await get_loads_reference_values(
                    variable_keys=[key for key in variable_keys if key is not None],
                    case=case,
                    session=session,
                )
                or []
            )
            for value in values:
                by_id_case[(key_to_id.get(value.id), case)] = value

    return [by_id_case.get((var_id, case), None) for var_id, case in keys]


async def get_variables(
    ids: Sequence[str], context: LoadsContext
) -> list[VariableType | None]:
    variables = model_get_variables(ids)
    vars_by_id = {str(var.id): var for var in variables}
    result: list[None | VariableType] = [vars_by_id.get(var_id) for var_id in ids]

    return result


async def get_reference_values_by_case_id(
    load_case_ids: Sequence[strawberry.ID], context: LoadsContext
) -> list[list[ReferenceValue]]:
    ids = [str(load_case_id) for load_case_id in load_case_ids]

    async with context.sessionmanager.session() as session:
        by_case_id = await get_reference_values_by_case_ids(ids, session)

    return [by_case_id.get(load_case_id, []) for load_case_id in ids]


async def get_sails_by_case_id(
    load_case_ids: Sequence[strawberry.ID], context: LoadsContext
) -> list[list[SailType]]:
    ids = [str(load_case_id) for load_case_id in load_case_ids]

    async with context.sessionmanager.session() as session:
        by_case_id = await get_sails_by_case_ids(ids, session)

    return [by_case_id.get(load_case_id, []) for load_case_id in ids]


async def get_context(
    messaging: Annotated[Messaging, Depends(get_messaging)],
) -> LoadsContext:
    context = LoadsContext(
        messaging=messaging,
        sessionmanager=sessionmanager,
        reference_by_case_input_loader=DataLoader(
            load_fn=lambda keys: get_reference_values(keys, context),  # type: ignore
            cache=False,
        ),
        reference_by_case_id_loader=DataLoader(
            load_fn=lambda keys: get_reference_values_by_case_id(keys, context),  # type: ignore
            cache=False,
        ),
        sails_by_case_id_loader=DataLoader(
            load_fn=lambda keys: get_sails_by_case_id(keys, context),  # type: ignore
            cache=False,
        ),
        variables_loader=DataLoader(
            load_fn=lambda keys: get_variables(keys, context),  # type: ignore
            cache=False,
        ),
    )

    return context
