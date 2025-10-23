from asyncio import Task, create_task
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from inspect import isclass
import logging
import sys
from typing import (
    Annotated,
    Callable,
    Coroutine,
    get_args,
)
from fastapi import Depends, FastAPI
from pydantic import Field, create_model
from strawberry.schema_directive import Location
import strawberry
from strawberry.fastapi import GraphQLRouter, BaseContext

from thrs.control.modules.thrusters import ThrustersParameters
from thrs.graphql.messaging import Messaging
from thrs.input_output.definitions.units import unit_for_annotation
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
import thrs.input_output.definitions.sensor as sensor
import thrs.input_output.definitions.control as control
from thrs.input_output.base import Stamped, ThrsModel
from pydantic.fields import FieldInfo
from aiomqtt import Client as MqttClient

from thrs.orchestration.config import Config


logger = logging.getLogger(__name__)


@strawberry.schema_directive(locations=[Location.FIELD_DEFINITION])
class JsonSchemaDirective:
    yard_tag: str | None = None
    component_type: str | None = None
    valve_type: str | None = None


@strawberry.experimental.pydantic.type(
    model=Stamped, all_fields=True, json_schema_directive=JsonSchemaDirective
)
class StampedType[T]:
    pass


def get_members(module):
    if hasattr(module, "__all__"):
        names = module.__all__
    else:
        names = dir(module)
    return {name: getattr(module, name) for name in names}


def convert_module(module, class_name_prefix: str):
    for name, cls in get_members(module).items():
        if isclass(cls) and issubclass(cls, ThrsModel):
            gql_cls = type(f"{class_name_prefix}{name}Type", (object,), {})
            strawberry.experimental.pydantic.type(
                model=cls, all_fields=True, json_schema_directive=JsonSchemaDirective
            )(gql_cls)


convert_module(sensor, "Sensor")
convert_module(control, "Control")


@strawberry.experimental.pydantic.type(
    model=ThrustersSensorValues,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class ThrustersSensorValuesType:
    pass


@strawberry.experimental.pydantic.type(
    model=ThrustersControlValues,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class ThrustersControlValuesType:
    pass


@strawberry.experimental.pydantic.type(
    model=ThrustersParameters,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class ThrustersParametersType:
    pass


DedataframedSimulationInputs = ThrustersSimulationInputs.dedataframe()
DedataframedSimulationOutputs = ThrustersSimulationOutputs.dedataframe()

_dedataframed_strawberries = {}


def ensure_dedataframe(annotation):
    if existing := _dedataframed_strawberries.get(annotation, None):
        return existing
    else:
        gql_cls = type(f"{annotation.__name__}SimulationType", (object,), {})
        strawberry.experimental.pydantic.type(
            model=annotation, all_fields=True, json_schema_directive=JsonSchemaDirective
        )(gql_cls)
        _dedataframed_strawberries[annotation] = gql_cls
        return gql_cls


for cls in [DedataframedSimulationInputs, DedataframedSimulationOutputs]:
    for name, field in cls.model_fields.items():
        ensure_dedataframe(field.annotation)


@strawberry.experimental.pydantic.type(
    model=DedataframedSimulationInputs,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class ThrustersSimulationInputsType:
    pass


@strawberry.experimental.pydantic.type(
    model=DedataframedSimulationOutputs,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class ThrustersSimulationOutputsType:
    pass


@strawberry.type
class ModuleSimulation[SimulationInput, SimulationOutput]:
    inputs: SimulationInput
    outputs: SimulationOutput


@strawberry.type
class Module[
    SensorValues,
    ControlValues,
    Parameters,
    SimulationInput,
    SimulationOutput,
]:
    sensor_values: SensorValues | None
    control_values: ControlValues | None
    parameters: Parameters
    simulation: ModuleSimulation[SimulationInput, SimulationOutput] | None = None


@strawberry.type
class Modules:
    thrusters: Module[
        ThrustersSensorValuesType,
        ThrustersControlValuesType,
        ThrustersParametersType,
        ThrustersSimulationInputsType,
        ThrustersSimulationOutputsType,
    ]


@strawberry.type
class SimulationState:
    time: datetime
    status: str


@strawberry.type
class ControlState:
    automatic: bool


@dataclass
class ThrsContext(BaseContext):
    messaging: Messaging[ThrustersSensorValues, ThrustersControlValues]


@strawberry.type
class Query:
    @strawberry.field()
    def modules(self, info: strawberry.Info[ThrsContext]) -> Modules:
        return Modules(
            thrusters=Module(
                sensor_values=ThrustersSensorValuesType.from_pydantic(
                    info.context.messaging.sensor_values
                )
                if info.context.messaging.sensor_values
                else None,
                control_values=ThrustersControlValuesType.from_pydantic(
                    info.context.messaging.control_values
                )
                if info.context.messaging.control_values
                else None,
                parameters=ThrustersParametersType.from_pydantic(
                    ThrustersParameters()
                ),  # TODO: ZERO-878 implement parameter setting and passage to simulation
                simulation=ModuleSimulation(
                    inputs=ThrustersSimulationInputsType.from_pydantic(
                        DedataframedSimulationInputs.zero(),  # TODO: ZERO-825 implement simulation input setting and passage to simulation
                    ),
                    outputs=ThrustersSimulationOutputsType.from_pydantic(
                        DedataframedSimulationOutputs.zero()  # TODO: ZERO-825 implement simulation output setting and passage to simulation
                    ),
                ),
            ),
        )

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

    @strawberry.field()
    def thrusters_sensor_values(self) -> ThrustersSensorValuesType:
        return ThrustersSensorValuesType.from_pydantic(ThrustersSensorValues.zero())


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
            model=input_model, all_fields=True
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


class DynamicInputFields:
    def __init_subclass__(cls):
        def _make_control_mutation(name: str, component_type: type):
            async def _mutation(
                self,
                component: component_type,  # type: ignore
                info: strawberry.Info[ThrsContext],
            ) -> ThrustersControlValuesType:
                control_values = info.context.messaging.control_values
                if control_values is None:
                    raise Exception("No control values available to modify")
                pydantic_value = component.to_pydantic().to_stamped()
                setattr(control_values, name, pydantic_value)
                expect = info.context.messaging.wait_for_control_values(
                    lambda v: getattr(v, name) == pydantic_value, timeout=2.0
                )
                await info.context.messaging.send_manual_controls(control_values)
                await expect
                return ThrustersControlValuesType.from_pydantic(control_values)

            return _mutation

        for name, field in ThrustersControlValues.model_fields.items():
            fn = generate_mutation_for_field(
                ThrustersControlValuesType,
                f"thrusters_control_{name}",
                name,
                field,
                _make_control_mutation,
                unstamp=True,
            )
            method = strawberry.mutation(fn)
            setattr(cls, fn.__name__, method)

        def _make_parameter_mutation(name: str, component_type: type):
            async def _mutation(
                self,
                value: component_type,  # type: ignore
                info: strawberry.Info[ThrsContext],
            ) -> ThrustersParametersType:
                parameters = info.context.messaging.parameters
                if parameters is None:
                    raise Exception("No parameters available to update")
                setattr(parameters, name, value)
                expect = info.context.messaging.wait_for_parameters(
                    lambda parameters: getattr(parameters, name) == value, timeout=2
                )
                await info.context.messaging.set_parameters(parameters)
                await expect
                return ThrustersParametersType.from_pydantic(parameters)

            return _mutation

        for name, field in ThrustersParameters.model_fields.items():
            fn = generate_mutation_for_field(
                ThrustersParametersType,
                f"thrusters_parameter_{name}",
                name,
                field,
                _make_parameter_mutation,
                unstamp=False,
            )
            method = strawberry.mutation(fn)
            setattr(cls, fn.__name__, method)

        def _make_simulation_input_mutation(name: str, component_type: type):
            async def _mutation(
                self,
                component: component_type,  # type: ignore
                info: strawberry.Info[ThrsContext],
            ) -> ThrustersSimulationInputsType:
                inputs = info.context.messaging.simulation_inputs
                if inputs is None:
                    raise Exception("No simulation inputs available to modify")
                pydantic_value = component.to_pydantic().to_stamped()
                setattr(inputs, name, pydantic_value)

                expect = info.context.messaging.wait_for_simulation_inputs(
                    lambda inputs: getattr(inputs, name) == pydantic_value,
                    timeout=2,
                )
                await info.context.messaging.set_simulation_inputs(inputs)
                await expect
                return ThrustersSimulationInputsType.from_pydantic(inputs)

            return _mutation

        for name, field in ThrustersSimulationInputs.model_fields.items():
            fn = generate_mutation_for_field(
                ThrustersControlValuesType,
                f"thrusters_simulation_{name}",
                name,
                field,
                _make_simulation_input_mutation,
                unstamp=True,
            )
            method = strawberry.mutation(fn)
            setattr(cls, fn.__name__, method)


@strawberry.type
class Mutation(DynamicInputFields):
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


type FieldMutation[T] = """Callable[
    [Mutation, object, strawberry.Info[ThrsContext]],
    Coroutine[None, None, T],
]"""

type ThrustersMessaging = Messaging[ThrustersSensorValues, ThrustersControlValues]


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Config()  # type: ignore
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt:
        messaging = Messaging(mqtt, ThrustersSensorValues, ThrustersControlValues)
        run_task = create_task(await messaging.run())

        def _finish(task: Task):
            if err := task.exception():
                logger.critical("Messaging failed", exc_info=err)
                sys.exit(1)

        run_task.add_done_callback(_finish)
        app.state.messaging = messaging
        yield
        run_task.cancel()


app = FastAPI(lifespan=lifespan)


def messaging() -> ThrustersMessaging:
    return app.state.messaging


async def get_context(
    messaging: "Annotated[ThrustersMessaging, Depends(messaging)]",
):
    return ThrsContext(messaging=messaging)


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
)

app.include_router(graphql_app, prefix="/graphql")
