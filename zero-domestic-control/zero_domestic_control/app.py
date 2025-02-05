from dataclasses import dataclass
from typing import Annotated
from aiomqtt import Client
from fastapi import Depends, FastAPI
import strawberry
from strawberry.schema.config import StrawberryConfig


from strawberry.fastapi import GraphQLRouter, BaseContext

from zero_domestic_control.config import Settings
from zero_domestic_control.mqtt import Blind, LightingGroup, Mqtt, Room

settings = Settings()


@dataclass
class MyContext(BaseContext):
    mqtt: Mqtt


async def mqtt():
    async with Client(settings.mqtt_host, 1883) as client:
        yield Mqtt(client)


async def get_context(
    mqtt: Annotated[Mqtt, Depends(mqtt)],
) -> MyContext:
    return MyContext(mqtt)


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
        await info.context.mqtt.send_room(
            Room(
                id=id,
                actual_temperature=temperature,
                temperature_setpoint=temperature,
                actual_humidity=None,
                amplifier_on=None,
            )
        )

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
        await info.context.mqtt.send_blind(Blind(id=id, level=level))

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
        await info.context.mqtt.send_lighting_group(LightingGroup(id=id, level=level))

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
            await info.context.mqtt.send_lighting_group(
                LightingGroup(id=lighting_group_id, level=level)
            )

    @strawberry.mutation
    async def set_amplifier(
        self, info: strawberry.Info[MyContext], id: strawberry.ID, on: bool
    ) -> None:
        await info.context.mqtt.send_room(
            Room(
                id=id,
                actual_temperature=None,
                temperature_setpoint=None,
                actual_humidity=None,
                amplifier_on=on,
            )
        )


schema = strawberry.Schema(
    query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=False)
)
app = FastAPI()
app.include_router(
    GraphQLRouter(schema=schema, context_getter=get_context), prefix="/graphql"
)
