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
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic.fields import FieldInfo
from strawberry.fastapi import GraphQLRouter

import thrs.graphql.consumers as consumers
import thrs.graphql.dhw as dhw
import thrs.graphql.pcm as pcm
import thrs.graphql.pvt as pvt
import thrs.graphql.simulation as simulation
import thrs.graphql.thrusters as thrusters
from thrs.control.modules.adsorption import ADSORPTION_MODULE_DESCRIPTION
from thrs.control.modules.consumers import CONSUMERS_MODULE_DESCRIPTION
from thrs.control.modules.dc import DC_MODULE_DESCRIPTION
from thrs.control.modules.dhw import DHW_MODULE_DESCRIPTION
from thrs.control.modules.drives import DRIVES_MODULE_DESCRIPTION
from thrs.control.modules.pcm import PCM_MODULE_DESCRIPTION
from thrs.control.modules.pvt import PVT_MODULE_DESCRIPTION
from thrs.control.modules.thrusters import THRUSTERS_MODULE_DESCRIPTION
from thrs.control.switching import AutomationMode
from thrs.graphql.base import (
    AdsorptionMessaging,
    ConsumersMessaging,
    DcMessaging,
    DhwMessaging,
    DrivesMessaging,
    FieldMutation,
    PcmMessaging,
    PvtMessaging,
    ThrsContext,
    ThrustersMessaging,
)
from thrs.graphql.consumers import ConsumersModule, ConsumersMutations
from thrs.graphql.dhw import DhwModule, DhwMutations
from thrs.graphql.helpers import ensure_input_type
from thrs.graphql.messaging import (
    ControlMessaging,
    DirectiveMessaging,
    SimulationMessaging,
)
from thrs.graphql.pcm import PcmModule, PcmMutations
from thrs.graphql.pvt import PvtModule, PvtMutations
from thrs.graphql.simulation import (
    SimulationInputsType,
    SimulationMutations,
    SimulationOutputsType,
)
from thrs.graphql.thrusters import ThrustersModule, ThrustersMutations
from thrs.orchestration.comms import (
    ControlApiChannels,
    ControlApiChannelsDescription,
    DirectivesApiChannels,
    DirectivesApiChannelsDescription,
    MqttConnector,
    SimulationApiChannels,
    SimulationApiChannelsDescription,
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
    def dhw(self, info: strawberry.Info[ThrsContext]) -> DhwModule:
        return dhw.resolve_module(info.context.dhw_messaging)


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
    DhwMutations,
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


def messaging(request: Request) -> DirectiveMessaging:
    return request.app.state.messaging


def thrusters_messaging(request: Request) -> ThrustersMessaging:
    return request.app.state.thrusters_messaging


def pvt_messaging(request: Request) -> PvtMessaging:
    return request.app.state.pvt_messaging


def pcm_messaging(request: Request) -> PcmMessaging:
    return request.app.state.pcm_messaging


def consumers_messaging(request: Request) -> ConsumersMessaging:
    return request.app.state.consumers_messaging


def dhw_messaging(request: Request) -> DhwMessaging:
    return request.app.state.dhw_messaging


def simulation_messaging(request: Request) -> SimulationMessaging:
    return request.app.state.simulation_messaging


async def get_context(
    messaging: Annotated[DirectiveMessaging, Depends(messaging)],
    thrusters_messaging: Annotated[ThrustersMessaging, Depends(thrusters_messaging)],
    pvt_messaging: Annotated[PvtMessaging, Depends(pvt_messaging)],
    pcm_messaging: Annotated[PcmMessaging, Depends(pcm_messaging)],
    consumers_messaging: Annotated[ConsumersMessaging, Depends(consumers_messaging)],
    dhw_messaging: Annotated[DhwMessaging, Depends(dhw_messaging)],
    simulation_messaging: Annotated[SimulationMessaging, Depends(simulation_messaging)],
):
    return ThrsContext(
        messaging=messaging,
        thrusters_messaging=thrusters_messaging,
        pvt_messaging=pvt_messaging,
        pcm_messaging=pcm_messaging,
        consumers_messaging=consumers_messaging,
        dhw_messaging=dhw_messaging,
        simulation_messaging=simulation_messaging,
    )


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema, context_getter=get_context)


def create_app(settings: Config):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt:
            messaging_connector = MqttConnector(mqtt)

            (
                thrusters_channels,
                pvt_channels,
                pcm_channels,
                consumers_channels,
                adsorption_channels,
                drives_channels,
                dc_channels,
                dhw_channels,
                simulation_channels,
                directives_channels,
            ) = (
                messaging_connector.build()
                .add(
                    ControlApiChannels,
                    ControlApiChannelsDescription.from_settings(
                        settings,
                        module_name="thrusters",
                        module_description=THRUSTERS_MODULE_DESCRIPTION,
                        automation_mode_cls=AutomationMode,
                    ),
                )
                .add(
                    ControlApiChannels,
                    ControlApiChannelsDescription.from_settings(
                        settings,
                        module_name="pvt",
                        module_description=PVT_MODULE_DESCRIPTION,
                        automation_mode_cls=AutomationMode,
                    ),
                )
                .add(
                    ControlApiChannels,
                    ControlApiChannelsDescription.from_settings(
                        settings,
                        module_name="pcm",
                        module_description=PCM_MODULE_DESCRIPTION,
                        automation_mode_cls=AutomationMode,
                    ),
                )
                .add(
                    ControlApiChannels,
                    ControlApiChannelsDescription.from_settings(
                        settings,
                        module_name="consumers",
                        module_description=CONSUMERS_MODULE_DESCRIPTION,
                        automation_mode_cls=AutomationMode,
                    ),
                )
                .add(
                    ControlApiChannels,
                    ControlApiChannelsDescription.from_settings(
                        settings,
                        module_name="adsorption",
                        module_description=ADSORPTION_MODULE_DESCRIPTION,
                        automation_mode_cls=AutomationMode,
                    ),
                )
                .add(
                    ControlApiChannels,
                    ControlApiChannelsDescription.from_settings(
                        settings,
                        module_name="drives",
                        module_description=DRIVES_MODULE_DESCRIPTION,
                        automation_mode_cls=AutomationMode,
                    ),
                )
                .add(
                    ControlApiChannels,
                    ControlApiChannelsDescription.from_settings(
                        settings,
                        module_name="dc",
                        module_description=DC_MODULE_DESCRIPTION,
                        automation_mode_cls=AutomationMode,
                    ),
                )
                .add(
                    ControlApiChannels,
                    ControlApiChannelsDescription.from_settings(
                        settings,
                        module_name="dhw",
                        module_description=DHW_MODULE_DESCRIPTION,
                        automation_mode_cls=AutomationMode,
                    ),
                )
                .add(
                    SimulationApiChannels,
                    SimulationApiChannelsDescription.from_settings(
                        settings,
                        simulation_inputs_cls=tuple(
                            dict.fromkeys(
                                inputs for inputs, _ in simulation.io_mapping.values()
                            )
                        ),
                        simulation_outputs_cls=tuple(
                            dict.fromkeys(
                                outputs for _, outputs in simulation.io_mapping.values()
                            )
                        ),
                    ),
                )
                .add(
                    DirectivesApiChannels,
                    DirectivesApiChannelsDescription.from_settings(settings),
                )
                .register()
            )

            thrusters_messaging: ThrustersMessaging = ControlMessaging(
                "thrusters",
                THRUSTERS_MODULE_DESCRIPTION,
                thrusters_channels,
            )
            pvt_messaging: PvtMessaging = ControlMessaging(
                "pvt",
                PVT_MODULE_DESCRIPTION,
                pvt_channels,
            )
            pcm_messaging: PcmMessaging = ControlMessaging(
                "pcm",
                PCM_MODULE_DESCRIPTION,
                pcm_channels,
            )
            consumers_messaging: ConsumersMessaging = ControlMessaging(
                "consumers",
                CONSUMERS_MODULE_DESCRIPTION,
                consumers_channels,
            )
            adsorption_messaging: AdsorptionMessaging = ControlMessaging(
                "adsorption",
                ADSORPTION_MODULE_DESCRIPTION,
                adsorption_channels,
            )
            drives_messaging: DrivesMessaging = ControlMessaging(
                "drives",
                DRIVES_MODULE_DESCRIPTION,
                drives_channels,
            )
            dc_messaging: DcMessaging = ControlMessaging(
                "dc",
                DC_MODULE_DESCRIPTION,
                dc_channels,
            )
            dhw_messaging: DhwMessaging = ControlMessaging(
                "dhw",
                DHW_MODULE_DESCRIPTION,
                dhw_channels,
            )
            simulation_messaging: SimulationMessaging = SimulationMessaging(
                simulation_channels,
            )
            messaging = DirectiveMessaging(
                [
                    thrusters_messaging,
                    pvt_messaging,
                    pcm_messaging,
                    adsorption_messaging,
                    consumers_messaging,
                    drives_messaging,
                    dc_messaging,
                    dhw_messaging,
                ],
                simulation_messaging,
                directives_channels,
                messaging_connector,
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
            app.state.adsorption_messaging = adsorption_messaging
            app.state.drives_messaging = drives_messaging
            app.state.dc_messaging = dc_messaging
            app.state.dhw_messaging = dhw_messaging
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

    app.include_router(graphql_app, prefix="/graphql")

    return app
