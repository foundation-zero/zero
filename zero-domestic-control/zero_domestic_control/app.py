from dataclasses import dataclass
from typing import Annotated
from aiomqtt import Client as MqttClient
from fastapi import Depends, FastAPI
import strawberry
from strawberry.schema.config import StrawberryConfig
from asyncio import TaskGroup

from strawberry.fastapi import GraphQLRouter, BaseContext
from fastapi import Request
from zero_domestic_control.services.ac import Ac
from zero_domestic_control.services.av import Av, Gude
from zero_domestic_control.config import Settings
from zero_domestic_control.services.hass import Hass
from zero_domestic_control.mqtt import (
    ControlSend,
    DataCollection,
)
from zero_domestic_control.messages import (
    Blind,
    LightingGroup,
)
import logging
import os
from typing import Callable
from functools import wraps
from typing import TypeVar, ParamSpec
from typing import Awaitable

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())

settings = Settings()
logger = logging.getLogger(__name__)


@dataclass
class MyContext(BaseContext):
    data_collection: DataCollection
    hass: Hass
    av: Av
    ac: Ac


async def mqtt_client():
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


async def data_collection(mqtt_client: Annotated[MqttClient, Depends(mqtt_client)]):
    yield DataCollection(mqtt_client)


async def hass_client():
    async with Hass.init_from_settings(settings) as hass:
        yield hass


async def av(
    mqtt_client: Annotated[MqttClient, Depends(mqtt_client)],
    data_collection: Annotated[DataCollection, Depends(data_collection)],
):
    yield Av(Gude(mqtt_client), data_collection)


async def ac(mqtt_client: Annotated[MqttClient, Depends(mqtt_client)]):
    yield Ac(ControlSend(mqtt_client))


async def get_context(
    data_collection: Annotated[DataCollection, Depends(data_collection)],
    hass_client: Annotated[Hass, Depends(hass_client)],
    av: Annotated[Av, Depends(av)],
    ac: Annotated[Ac, Depends(ac)],
) -> MyContext:
    return MyContext(data_collection, hass_client, av, ac)


@strawberry.type
class MutationResponse:
    code: int
    success: bool
    message: str


@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return "1.0.0"


P = ParamSpec("P")
R = TypeVar("R")


def raise_taskgroup_exception(
    func: Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[R]]:
    """Decorator that re-raises exceptions raised inside a taskgroup."""

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await func(*args, **kwargs)
        except* Exception as egroup:
            raise egroup.exceptions[0]

    return wrapper


@strawberry.type
class Mutation:
    @strawberry.mutation
    @raise_taskgroup_exception
    async def set_room_temperature_setpoints(
        self,
        info: strawberry.Info[MyContext],
        ids: list[strawberry.ID],
        temperature: Annotated[
            float,
            strawberry.argument(description="desired temperature in degrees Celsius"),
        ],
    ) -> MutationResponse:
        info.context.ac.validate_room_ids([str(id) for id in ids])

        async with TaskGroup() as tg:
            for room_id in ids:
                tg.create_task(
                    info.context.ac.write_room_temperature_setpoint(
                        room=room_id, temperature=temperature
                    )
                )

        return MutationResponse(
            code=200,
            success=True,
            message=f"Temperature setpoint for room(s) {ids} set to {temperature}°C",
        )

    @strawberry.mutation
    @raise_taskgroup_exception
    async def set_room_humidity_setpoints(
        self,
        info: strawberry.Info[MyContext],
        ids: list[strawberry.ID],
        humidity: Annotated[
            float,
            strawberry.argument(
                description="desired humidity in relative humidity percentage"
            ),
        ],
    ) -> MutationResponse:
        info.context.ac.validate_room_ids([str(id) for id in ids])
        async with TaskGroup() as tg:
            for room_id in ids:
                tg.create_task(
                    info.context.ac.write_room_humidity_setpoint(
                        room=room_id, humidity=humidity
                    )
                )
        return MutationResponse(
            code=200,
            success=True,
            message=f"Humidity setpoint for room(s) {ids} set to {humidity}",
        )

    @strawberry.mutation
    @raise_taskgroup_exception
    async def set_room_co2_setpoint(
        self,
        info: strawberry.Info[MyContext],
        ids: list[strawberry.ID],
        co2: Annotated[
            float,
            strawberry.argument(description="desired CO2 level in ppm"),
        ],
    ) -> MutationResponse:
        info.context.ac.validate_room_ids([str(id) for id in ids])
        async with TaskGroup() as tg:
            for room_id in ids:
                tg.create_task(
                    info.context.ac.write_room_co2_setpoint(room=room_id, co2=co2)
                )
        return MutationResponse(
            code=200,
            success=True,
            message=f"CO2 setpoint for room(s) {ids} set to {co2} ppm",
        )

    @strawberry.mutation
    @raise_taskgroup_exception
    async def set_blinds(
        self,
        info: strawberry.Info[MyContext],
        ids: list[strawberry.ID],
        level: Annotated[
            float,
            strawberry.argument(description="desired brightness as ratio 0..1"),
        ],
    ) -> MutationResponse:
        info.context.hass.validate_blind_group_ids([str(id) for id in ids])
        async with TaskGroup() as tg:
            for room_id in ids:
                tg.create_task(
                    info.context.hass.set_blind(Blind(id=room_id, level=level))
                )
        return MutationResponse(
            code=200,
            success=True,
            message=f"Blind(s) {ids} set to {level}",
        )

    @strawberry.mutation
    @raise_taskgroup_exception
    async def set_lighting_groups(
        self,
        info: strawberry.Info[MyContext],
        level: Annotated[
            float,
            strawberry.argument(description="desired brightness as ratio 0..1"),
        ],
        ids: list[strawberry.ID] | None,
    ) -> MutationResponse:
        if ids is not None:
            info.context.hass.validate_lighting_group_ids([str(id) for id in ids])
            async with TaskGroup() as tg:
                for lighting_group_id in ids:
                    tg.create_task(
                        info.context.hass.set_lighting_group(
                            LightingGroup(id=lighting_group_id, level=level)
                        )
                    )
            return MutationResponse(
                code=200,
                success=True,
                message=f"Lighting group(s) {ids} set to {level}",
            )
        else:
            await info.context.hass.set_lighting_group_all(level=level)
            return MutationResponse(
                code=200,
                success=True,
                message=f"All lighting groups set to {level}",
            )

    @strawberry.mutation
    @raise_taskgroup_exception
    async def set_amplifiers(
        self, ids: list[strawberry.ID], info: strawberry.Info[MyContext], on: bool
    ) -> MutationResponse:
        info.context.av.validate_room_ids([str(id) for id in ids])
        async with TaskGroup() as tg:
            for room_id in ids:
                tg.create_task(info.context.av.set_amplifier(room_id, on=on))
        return MutationResponse(
            code=200,
            success=True,
            message=f"Amplifier(s) {ids} set to {'on' if on else 'off'}",
        )


schema = strawberry.Schema(
    query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=True)
)
app = FastAPI()
app.include_router(
    GraphQLRouter(schema=schema, context_getter=get_context),
    prefix="/graphql",
)


@app.middleware("http")
async def log_request(request: Request, call_next):
    body = (await request.body()).decode("utf-8")
    clean_body = body.replace("\n", "").replace("\r", "").strip()
    logger.info(f"Request: {clean_body}")
    response = await call_next(request)
    return response
