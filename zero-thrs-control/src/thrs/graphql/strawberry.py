from asyncio import Task, create_task
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import sys
from typing import (
    Annotated,
    Callable,
    get_args,
)
from fastapi import Depends, FastAPI
from pydantic import Field, create_model
import strawberry
from strawberry.fastapi import GraphQLRouter

from thrs.control.modules.consumers import ConsumersParameters
from thrs.control.modules.pcm import PcmParameters
from thrs.control.modules.pvt import PvtParameters
from thrs.control.modules.thrusters import ThrustersParameters
from thrs.graphql.base import (
    ConsumersMessaging,
    FieldMutation,
    PcmMessaging,
    PvtMessaging,
    ThrsContext,
    ThrustersMessaging,
)
from thrs.graphql.messaging import Messaging, MessagingModule
from thrs.graphql.pvt import PvtModule, PvtMutations
from thrs.graphql.thrusters import ThrustersModule, ThrustersMutations
from thrs.graphql.pcm import PcmModule, PcmMutations
from thrs.graphql.consumers import ConsumersModule, ConsumersMutations

from thrs.input_output.definitions.units import unit_for_annotation
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
import thrs.graphql.thrusters as thrusters
import thrs.graphql.pvt as pvt
import thrs.graphql.pcm as pcm
import thrs.graphql.consumers as consumers
from thrs.input_output.base import Stamped, ThrsModel
from pydantic.fields import FieldInfo
from aiomqtt import Client as MqttClient

from thrs.orchestration.config import Config


logger = logging.getLogger(__name__)


@strawberry.type
class Modules:
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


@strawberry.type
class SimulationState:
    time: datetime
    status: str


@strawberry.type
class ControlState:
    automatic: bool


@strawberry.type
class Query:
    @strawberry.field()
    def modules(self, info: strawberry.Info[ThrsContext]) -> Modules:
        return Modules()

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

    @strawberry.field
    def control(self, info: strawberry.Info[ThrsContext]) -> ControlState | None:
        if info.context.messaging.control_status is None:
            return None
        return ControlState(automatic=info.context.messaging.control_status.automatic)


_input_types = {}


class UnstampedInput(ThrsModel):
    @staticmethod
    def generate_for_model(name: str, model: type[ThrsModel]):
        fields = {
            key: Annotated[
                get_args(unit)[0] if get_args(unit) else unit,
                Field(),
            ]
            for key, field in model.model_fields.items()
            if (unit := unit_for_annotation(field.annotation))
        }
        unstamped_model = create_model(name, **fields, __base__=UnstampedInput)  # type: ignore
        unstamped_model._MODEL = model
        return unstamped_model

    def to_stamped(self):
        values = {
            key: Stamped.stamp(getattr(self, key))
            for key in type(self).model_fields.keys()
        }
        return self._MODEL(**values)  # type: ignore


def ensure_input_type(annotation, *args, unstamp: bool) -> type:
    if existing := _input_types.get(annotation.__name__, None):
        return existing
    elif unstamp:
        input_model = UnstampedInput.generate_for_model(
            f"{annotation.__name__}InputType", annotation
        )
        input_type = strawberry.experimental.pydantic.input(
            model=input_model, all_fields=True, use_pydantic_alias=False
        )(type(f"{annotation.__name__}InputType", (object,), {}))
        _input_types[annotation.__name__] = input_type
        return input_type
    else:
        return annotation


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
class Mutation(ThrustersMutations, PvtMutations, PcmMutations, ConsumersMutations):
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

    @strawberry.mutation
    async def control_set_automation_mode(
        self, info: strawberry.Info[ThrsContext], automatic: bool
    ) -> None:
        await info.context.messaging.set_automation(automatic)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Config()  # type: ignore
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt:
        thrusters_messaging: ThrustersMessaging = MessagingModule(
            "thrusters",
            ThrustersSensorValues,
            ThrustersControlValues,
            ThrustersParameters,
            ThrustersSimulationInputs,
            ThrustersSimulationOutputs,
            mqtt,
        )
        pvt_messaging: PvtMessaging = MessagingModule(
            "pvt",
            PvtSensorValues,
            PvtControlValues,
            PvtParameters,
            PvtSimulationInputs,
            PvtSimulationOutputs,
            mqtt,
        )
        pcm_messaging: PcmMessaging = MessagingModule(
            "pcm",
            PcmSensorValues,
            PcmControlValues,
            PcmParameters,
            PcmSimulationInputs,
            PcmSimulationOutputs,
            mqtt,
        )
        consumers_messaging: ConsumersMessaging = MessagingModule(
            "consumers",
            ConsumersSensorValues,
            ConsumersControlValues,
            ConsumersParameters,
            ConsumersSimulationInputs,
            ConsumersSimulationOutputs,
            mqtt,
        )
        messaging = Messaging(
            mqtt,
            [thrusters_messaging, pvt_messaging, pcm_messaging, consumers_messaging],
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
        yield
        run_task.cancel()


app = FastAPI(lifespan=lifespan)


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


async def get_context(
    messaging: "Annotated[Messaging, Depends(messaging)]",
    thrusters_messaging: "Annotated[ThrustersMessaging, Depends(thrusters_messaging)]",
    pvt_messaging: "Annotated[PvtMessaging, Depends(pvt_messaging)]",
    pcm_messaging: "Annotated[PcmMessaging, Depends(pcm_messaging)]",
    consumers_messaging: "Annotated[ConsumersMessaging, Depends(consumers_messaging)]",
):
    return ThrsContext(
        messaging=messaging,
        thrusters_messaging=thrusters_messaging,
        pvt_messaging=pvt_messaging,
        pcm_messaging=pcm_messaging,
        consumers_messaging=consumers_messaging,
    )


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
)

app.include_router(graphql_app, prefix="/graphql")
