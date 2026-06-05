import logging
import sys
from asyncio import Task, create_task
from contextlib import asynccontextmanager
from datetime import datetime
from typing import (
    Annotated,
    Callable,
)

import strawberry
from aiomqtt import Client as MqttClient
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic.fields import FieldInfo
from strawberry.fastapi import GraphQLRouter

import thrs.graphql.boilers as boilers
import thrs.graphql.consumers as consumers
import thrs.graphql.pcm as pcm
import thrs.graphql.pvt as pvt
import thrs.graphql.simulation as simulation
import thrs.graphql.thrusters as thrusters
from thrs.control.modules.boilers import BoilersControlMode, BoilersParameters
from thrs.control.modules.consumers import ConsumersControlMode, ConsumersParameters
from thrs.control.modules.pcm import PcmControlMode, PcmParameters
from thrs.control.modules.pvt import PvtControlMode, PvtParameters
from thrs.control.modules.thrusters import ThrustersControlMode, ThrustersParameters
from thrs.graphql.base import (
    BoilersMessaging,
    ConsumersMessaging,
    FieldMutation,
    PcmMessaging,
    PvtMessaging,
    ThrsContext,
    ThrustersMessaging,
)
from thrs.graphql.boilers import (
    BoilersModule,
    BoilersMutations,
)
from thrs.graphql.consumers import (
    ConsumersModule,
    ConsumersMutations,
)
from thrs.graphql.helpers import ensure_input_type
from thrs.graphql.messaging import ControlMessaging, Messaging, SimulationMessaging
from thrs.graphql.pcm import (
    PcmModule,
    PcmMutations,
)
from thrs.graphql.pvt import (
    PvtModule,
    PvtMutations,
)
from thrs.graphql.simulation import (
    SimulationInputsType,
    SimulationMutations,
    SimulationOutputsType,
)
from thrs.graphql.thrusters import (
    ThrustersModule,
    ThrustersMutations,
)
from thrs.input_output.modules.boilers import BoilersControlValues, BoilersSensorValues
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
)
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
)
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
)
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
)
from thrs.orchestration.config import Config

logger = logging.getLogger(__name__)


@strawberry.type
class ControlModules:
    @strawberry.field
    def thrusters(self, info: strawberry.Info[ThrsContext]) -> ThrustersModule:
        return thrusters.resolve_module(info.context.thrusters_messaging)

    @strawberry.field
    def pvt(self, info: strawberry.Info[ThrsContext]) -> PvtModule:
        return pvt.resolve_module(info.context.pvt_messaging)

    @strawberry.field
    def pcm(self, info: strawberry.Info[ThrsContext]) -> PcmModule:
        return pcm.resolve_module(info.context.pcm_messaging)

    @strawberry.field
    def consumers(self, info: strawberry.Info[ThrsContext]) -> ConsumersModule:
        return consumers.resolve_module(info.context.consumers_messaging)

    @strawberry.field
    def boilers(self, info: strawberry.Info[ThrsContext]) -> BoilersModule:
        return boilers.resolve_module(info.context.boilers_messaging)


@strawberry.type
class SimulationState:
    time: datetime
    status: str

    @strawberry.field
    def inputs(self, info: strawberry.Info[ThrsContext]) -> SimulationInputsType | None:  # pyright: ignore[reportInvalidTypeForm]
        return simulation.resolve_inputs(info.context.simulation_messaging)

    @strawberry.field
    def outputs(
        self, info: strawberry.Info[ThrsContext]
    ) -> SimulationOutputsType | None:  # pyright: ignore[reportInvalidTypeForm]
        return simulation.resolve_outputs(info.context.simulation_messaging)


@strawberry.type
class ControlState:
    automatic: bool


@strawberry.type
class Query:
    @strawberry.field()
    def modules(self, info: strawberry.Info[ThrsContext]) -> ControlModules:
        return ControlModules()

    @strawberry.field
    def simulation(self, info: strawberry.Info[ThrsContext]) -> SimulationState | None:
        if (
            info.context.messaging.simulation_status is None
            or info.context.messaging.simulation_status.simulation_time is None
        ):
            return None
        return SimulationState(
            time=info.context.messaging.simulation_status.simulation_time,
            status=info.context.messaging.simulation_status.status,
        )


def generate_mutation_for_field[T](
    cls: type[T],
    name: str,
    field_name: str,
    field: FieldInfo,
    make_fn: "Callable[[str, type], FieldMutation[T]]",
    *args,
    unstamp: bool,
) -> "FieldMutation[T]":
    input_type = ensure_input_type(field.annotation, unstamp=unstamp)
    mutation = make_fn(field_name, input_type)
    mutation.__name__ = f"set_{name}"
    return mutation


@strawberry.type
class Mutation(
    ThrustersMutations,
    PvtMutations,
    PcmMutations,
    ConsumersMutations,
    BoilersMutations,
    SimulationMutations,
):
    @strawberry.mutation
    async def simulation_play(
        self, info: strawberry.Info[ThrsContext], playback_rate: float = 1.0
    ) -> None:
        if info.context.messaging.simulation_status is None:
            raise Exception("No simulation status available, cannot play")
        if info.context.messaging.simulation_status.status != "available":
            raise Exception("Can only play an available simulation")
        expect_status = info.context.messaging.wait_for_simulation_status(
            "running", timeout=2.0
        )
        await info.context.messaging.play_simulation(playback_rate)
        await expect_status

    @strawberry.mutation
    async def simulation_pause(self, info: strawberry.Info[ThrsContext]) -> None:
        if info.context.messaging.simulation_status is None:
            raise Exception("No simulation status available, cannot pause")
        if info.context.messaging.simulation_status.status != "running":
            raise Exception("Can only pause a running simulation")
        expect_status = info.context.messaging.wait_for_simulation_status(
            "available", timeout=2.0
        )
        await info.context.messaging.pause_simulation()
        await expect_status

    @strawberry.mutation
    async def simulation_step(
        self, info: strawberry.Info[ThrsContext], seconds: float
    ) -> None:
        if info.context.messaging.simulation_status is None:
            raise Exception("No simulation status available, cannot step")
        if info.context.messaging.simulation_status.status != "available":
            raise Exception("Can only step an available simulation")
        expect_status = info.context.messaging.wait_for_simulation_status(
            "stepping", timeout=2.0
        )
        await info.context.messaging.step_simulation(seconds)
        await expect_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Config()  # type: ignore
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt:
        thrusters_messaging: ThrustersMessaging = ControlMessaging(
            "thrusters",
            ThrustersSensorValues,
            ThrustersControlValues,
            ThrustersParameters,
            ThrustersControlMode,
            mqtt,
        )
        pvt_messaging: PvtMessaging = ControlMessaging(
            "pvt",
            PvtSensorValues,
            PvtControlValues,
            PvtParameters,
            PvtControlMode,
            mqtt,
        )
        pcm_messaging: PcmMessaging = ControlMessaging(
            "pcm",
            PcmSensorValues,
            PcmControlValues,
            PcmParameters,
            PcmControlMode,
            mqtt,
        )
        consumers_messaging: ConsumersMessaging = ControlMessaging(
            "consumers",
            ConsumersSensorValues,
            ConsumersControlValues,
            ConsumersParameters,
            ConsumersControlMode,
            mqtt,
        )
        boilers_messaging: BoilersMessaging = ControlMessaging(
            "boilers",
            BoilersSensorValues,
            BoilersControlValues,
            BoilersParameters,
            BoilersControlMode,
            mqtt,
        )
        simulation_messaging: SimulationMessaging = SimulationMessaging(
            simulation.io_mapping, mqtt
        )
        messaging = Messaging(
            mqtt,
            [
                thrusters_messaging,
                pvt_messaging,
                pcm_messaging,
                consumers_messaging,
                boilers_messaging,
            ],
            simulation_messaging,
        )
        run_task = create_task(await messaging.run())

        def _finish(task: Task):
            if err := task.exception():
                logger.critical("Messaging failed", exc_info=err)
                sys.exit(1)

        run_task.add_done_callback(_finish)
        app.state.messaging = messaging
        app.state.thrusters_messaging = thrusters_messaging
        app.state.pvt_messaging = pvt_messaging
        app.state.pcm_messaging = pcm_messaging
        app.state.consumers_messaging = consumers_messaging
        app.state.boilers_messaging = boilers_messaging
        app.state.simulation_messaging = simulation_messaging
        yield
        run_task.cancel()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def messaging() -> Messaging:
    return app.state.messaging


def thrusters_messaging() -> ThrustersMessaging:
    return app.state.thrusters_messaging


def pvt_messaging() -> PvtMessaging:
    return app.state.pvt_messaging


def pcm_messaging() -> PcmMessaging:
    return app.state.pcm_messaging


def consumers_messaging() -> ConsumersMessaging:
    return app.state.consumers_messaging


def boilers_messaging() -> BoilersMessaging:
    return app.state.boilers_messaging


def simulation_messaging() -> SimulationMessaging:
    return app.state.simulation_messaging


async def get_context(
    messaging: Annotated[Messaging, Depends(messaging)],
    thrusters_messaging: Annotated[ThrustersMessaging, Depends(thrusters_messaging)],
    pvt_messaging: Annotated[PvtMessaging, Depends(pvt_messaging)],
    pcm_messaging: Annotated[PcmMessaging, Depends(pcm_messaging)],
    consumers_messaging: Annotated[ConsumersMessaging, Depends(consumers_messaging)],
    boilers_messaging: Annotated[BoilersMessaging, Depends(boilers_messaging)],
    simulation_messaging: Annotated[SimulationMessaging, Depends(simulation_messaging)],
):
    return ThrsContext(
        messaging=messaging,
        thrusters_messaging=thrusters_messaging,
        pvt_messaging=pvt_messaging,
        pcm_messaging=pcm_messaging,
        consumers_messaging=consumers_messaging,
        boilers_messaging=boilers_messaging,
        simulation_messaging=simulation_messaging,
    )


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
)

app.include_router(graphql_app, prefix="/graphql")
