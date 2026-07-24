from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Annotated, assert_never
from contextlib import asynccontextmanager
from aiomqtt import Client as MqttClient
from domestic_control.history import (
    AcLog,
    AmplifiersLog,
    BlindsLog,
    GreptimeLog,
    LightingGroupsLog,
    VentilationLog,
)
from fastapi import Depends, FastAPI
from sqlalchemy import TextClause, text
import strawberry
from strawberry.schema.config import StrawberryConfig
from strawberry.dataloader import DataLoader
from asyncio import TaskGroup
from sqlalchemy.ext.asyncio import create_async_engine

from strawberry.fastapi import GraphQLRouter, BaseContext
from fastapi import Request
from domestic_control.services.ac import Ac
from domestic_control.services.av import Av, Gude
from domestic_control.services.ventilation import Ventilation
from domestic_control.config import Settings
from domestic_control.services.hass import Hass, id_to_room_id
from domestic_control.mqtt import (
    ControlSend,
    DataCollection,
)
from domestic_control.sink import CompositeSink, PostgresSink, Sink
from domestic_control.messages import (
    Blind,
    LightingGroup,
)
import logging
import os
import sys
from typing import Callable
from functools import partial, wraps
from typing import TypeVar, ParamSpec
from typing import Awaitable


from strawberry.experimental.pydantic.conversion_types import (
    StrawberryTypeFromPydantic,
)

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    stream=sys.stdout,
)

settings = Settings()  # type: ignore
logger = logging.getLogger(__name__)


class LogDataLoader:
    def __init__(self, engine):
        self._engine = engine
        self._loaders = {}

    def _create_loader(self, cls: type[GreptimeLog], period: "TimePeriod"):
        async def loader(
            cls: type[GreptimeLog], period: "TimePeriod", room_ids: list[str]
        ):
            result = await cls.query(
                engine=self._engine,
                room_ids=room_ids,
                start_time=period.start_time(),
                end_time=period.end_time(),
                period=period.interval_sql(),
            )
            return [result.get(room_id, []) for room_id in room_ids]

        self._loaders[(cls, period)] = DataLoader(load_fn=partial(loader, cls, period))
        return self._loaders[(cls, period)]

    async def load_log[T: GreptimeLog](
        self, cls: type[T], room_id: str, period: "TimePeriod"
    ) -> list[T]:
        loader = self._loaders.get((cls, period)) or self._create_loader(cls, period)
        return await loader.load(room_id)


@dataclass
class MyContext(BaseContext):
    data_collection: Sink
    hass: Hass
    av: Av
    ac: Ac
    ventilation: Ventilation
    log_data_loader: LogDataLoader


def log_data_loader(request: Request):
    return LogDataLoader(request.app.state.greptime_engine)


async def mqtt_client():
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


async def data_collection(
    request: Request,
    mqtt_client: Annotated[MqttClient, Depends(mqtt_client)],
):
    yield CompositeSink(
        begin_sinks=[PostgresSink(request.app.state.postgres_engine)],
        sinks=[
            DataCollection(mqtt_client),
        ],
    )


async def hass_client():
    async with Hass.init_from_settings(settings) as hass:
        yield hass


async def av(
    mqtt_client: Annotated[MqttClient, Depends(mqtt_client)],
    data_collection: Annotated[Sink, Depends(data_collection)],
):
    yield Av(Gude(mqtt_client), data_collection)


async def ac(mqtt_client: Annotated[MqttClient, Depends(mqtt_client)]):
    yield Ac(ControlSend(mqtt_client))


async def ventilation(mqtt_client: Annotated[MqttClient, Depends(mqtt_client)]):
    yield Ventilation(ControlSend(mqtt_client))


async def get_context(
    data_collection: Annotated[Sink, Depends(data_collection)],
    hass_client: Annotated[Hass, Depends(hass_client)],
    av: Annotated[Av, Depends(av)],
    ac: Annotated[Ac, Depends(ac)],
    ventilation: Annotated[Ventilation, Depends(ventilation)],
    log_data_loader: Annotated[LogDataLoader, Depends(log_data_loader)],
) -> MyContext:
    return MyContext(data_collection, hass_client, av, ac, ventilation, log_data_loader)


@strawberry.type
class MutationResponse:
    code: int
    success: bool
    message: str


@strawberry.enum
class TimePeriod(Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"

    def interval_sql(self) -> TextClause:
        if self == TimePeriod.HOUR:
            return text("INTERVAL 5 minutes")
        elif self == TimePeriod.DAY:
            return text("INTERVAL 1 hours")
        elif self == TimePeriod.WEEK:
            return text("INTERVAL 12 hours")
        else:
            assert_never(self)

    def start_time(self) -> datetime:
        if self == TimePeriod.HOUR:
            return self.end_time() - timedelta(hours=1)
        elif self == TimePeriod.DAY:
            return self.end_time() - timedelta(days=1)
        elif self == TimePeriod.WEEK:
            return self.end_time() - timedelta(weeks=1)
        else:
            assert_never(self)

    def end_time(self) -> datetime:
        return datetime.now(tz=timezone.utc)


def log_field[T: GreptimeLog](
    model: type[T], gmodel: type[StrawberryTypeFromPydantic[T]]
) -> Callable[
    ["Query", strawberry.Info[MyContext], strawberry.ID, TimePeriod],
    Awaitable[list[StrawberryTypeFromPydantic[T]]],
]:
    @strawberry.field(graphql_type=list[gmodel])
    async def resolver(
        self,
        info: strawberry.Info[MyContext],
        room_id: strawberry.ID,
        period: TimePeriod,
    ) -> list[StrawberryTypeFromPydantic[T]]:
        result = await info.context.log_data_loader.load_log(
            model, str(room_id), period
        )
        return [gmodel.from_pydantic(row) for row in result]

    return resolver


@strawberry.experimental.pydantic.type(model=AcLog)
class AcLogType:
    timestamp: strawberry.auto
    temperature_setpoint: strawberry.auto
    humidity_setpoint: strawberry.auto
    actual_temperature: strawberry.auto
    actual_humidity: strawberry.auto


@strawberry.experimental.pydantic.type(model=AmplifiersLog)
class AmplifiersLogType:
    timestamp: strawberry.auto
    id: strawberry.auto
    on: strawberry.auto


@strawberry.experimental.pydantic.type(model=VentilationLog)
class VentilationLogType:
    timestamp: strawberry.auto
    id: strawberry.auto
    co2_setpoint: strawberry.auto
    actual_co2: strawberry.auto


@strawberry.experimental.pydantic.type(model=BlindsLog)
class BlindsLogType:
    timestamp: strawberry.auto
    id: strawberry.auto
    room_id: strawberry.auto
    level: strawberry.auto


@strawberry.experimental.pydantic.type(model=LightingGroupsLog)
class LightingGroupsLogType:
    timestamp: strawberry.auto
    id: strawberry.auto
    room_id: strawberry.auto
    level: strawberry.auto


@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return "1.0.0"

    air_conditioning_log = log_field(AcLog, AcLogType)
    amplifiers_log = log_field(AmplifiersLog, AmplifiersLogType)
    ventilation_log = log_field(VentilationLog, VentilationLogType)
    blinds_log = log_field(BlindsLog, BlindsLogType)
    lighting_groups_log = log_field(LightingGroupsLog, LightingGroupsLogType)


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
    async def set_room_co2_setpoints(
        self,
        info: strawberry.Info[MyContext],
        ids: list[strawberry.ID],
        co2: Annotated[
            float,
            strawberry.argument(description="desired CO2 level in ppm"),
        ],
    ) -> MutationResponse:
        info.context.ventilation.validate_room_ids([str(id) for id in ids])
        async with TaskGroup() as tg:
            for room_id in ids:
                tg.create_task(
                    info.context.ventilation.write_room_co2_setpoint(
                        room=room_id, co2=co2
                    )
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
            for blind_id in ids:
                tg.create_task(
                    info.context.hass.set_blind(
                        Blind(id=blind_id, room_id=id_to_room_id(blind_id), level=level)
                    )
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
                            LightingGroup(
                                id=lighting_group_id,
                                room_id=id_to_room_id(lighting_group_id),
                                level=level,
                            )
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle including database engines and sinks."""
    # Startup

    app.state.postgres_engine = create_async_engine(settings.pg_url)
    app.state.greptime_engine = create_async_engine(settings.greptime_url_with_driver)

    logger.info("PostgreSQL engine initialized")
    logger.info(f"GreptimeDB engine initialized with URL: {settings.greptime_url}")

    yield

    # Shutdown
    await app.state.postgres_engine.dispose()
    await app.state.greptime_engine.dispose()
    logger.info("PostgreSQL and GreptimeDB engines disposed")


app = FastAPI(lifespan=lifespan)
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
