from dataclasses import dataclass
from typing import Annotated
from aiomqtt import Client as MqttClient
from fastapi import Depends, FastAPI
import strawberry
from strawberry.schema.config import StrawberryConfig


from strawberry.fastapi import GraphQLRouter, BaseContext

from zero_domestic_control.services.ac import Ac
from zero_domestic_control.services.av import Av, Gude
from zero_domestic_control.config import Settings
from zero_domestic_control.services.hass import Hass
from zero_domestic_control.mqtt import (
    Blind,
    ControlSend,
    DataCollection,
    LightingGroup,
)

import logging
import os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())

settings = Settings()


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
class Query:
    @strawberry.field
    def version(self) -> str:
        return "1.0.0"


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def set_room_temperature_setpoint(
        self,
        info: strawberry.Info[MyContext],
        id: strawberry.ID,
        temperature: Annotated[
            int,
            strawberry.argument(description="desired temperature in degrees Celsius"),
        ],
    ) -> None:
        await info.context.ac.write_room_temperature_setpoint(id, temperature)

    @strawberry.mutation
    async def set_blind(
        self,
        info: strawberry.Info[MyContext],
        id: strawberry.ID,
        level: Annotated[
            float,
            strawberry.argument(description="desired brightness as ratio 0..1"),
        ],
    ) -> None:
        await info.context.hass.set_blind(Blind(id=id, level=level))

    @strawberry.mutation
    async def set_lighting_group(
        self,
        info: strawberry.Info[MyContext],
        id: strawberry.ID,
        level: Annotated[
            float,
            strawberry.argument(description="desired brightness as ratio 0..1"),
        ],
    ) -> None:
        await info.context.hass.set_lighting_group(LightingGroup(id=id, level=level))

    @strawberry.mutation
    async def set_lighting_groups(
        self,
        info: strawberry.Info[MyContext],
        ids: list[strawberry.ID],
        level: Annotated[
            float,
            strawberry.argument(description="desired brightness as ratio 0..1"),
        ],
    ) -> None:
        for lighting_group_id in ids:
            await info.context.hass.set_lighting_group(
                LightingGroup(id=lighting_group_id, level=level)
            )

    @strawberry.mutation
    async def set_amplifier(
        self, info: strawberry.Info[MyContext], id: strawberry.ID, on: bool
    ) -> None:
        await info.context.av.set_amplifier(id, on)


schema = strawberry.Schema(
    query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=True)
)
app = FastAPI()
app.include_router(
    GraphQLRouter(schema=schema, context_getter=get_context), prefix="/graphql"
)
