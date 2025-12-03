from dataclasses import dataclass
from inspect import isclass
from typing import Annotated, Callable, Coroutine, get_args
from pydantic import Field, create_model
import strawberry
from thrs.control.modules.consumers import ConsumersParameters
from thrs.control.modules.pcm import PcmParameters
from thrs.control.modules.pvt import PvtParameters
from thrs.control.modules.thrusters import ThrustersParameters
from thrs.graphql.messaging import Messaging, MessagingModule
import thrs.input_output.definitions.sensor as sensor
import thrs.input_output.definitions.control as control
from strawberry.schema_directive import Location
from thrs.input_output.base import Stamped, ThrsModel
from strawberry.fastapi import BaseContext
from pydantic.fields import FieldInfo

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

type ThrustersMessaging = MessagingModule[
    ThrustersSensorValues,
    ThrustersControlValues,
    ThrustersParameters,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
]
type PvtMessaging = MessagingModule[
    PvtSensorValues,
    PvtControlValues,
    PvtParameters,
    PvtSimulationInputs,
    PvtSimulationOutputs,
]

type PcmMessaging = MessagingModule[
    PcmSensorValues,
    PcmControlValues,
    PcmParameters,
    PcmSimulationInputs,
    PcmSimulationOutputs,
]

type ConsumersMessaging = MessagingModule[
    ConsumersSensorValues,
    ConsumersControlValues,
    ConsumersParameters,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
]


@strawberry.schema_directive(locations=[Location.FIELD_DEFINITION])
class JsonSchemaDirective:
    yard_tag: str | None = None
    component_type: str | None = None
    valve_type: str | None = None


@strawberry.experimental.pydantic.type(
    model=Stamped,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
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
                model=cls,
                all_fields=True,
                json_schema_directive=JsonSchemaDirective,
                use_pydantic_alias=False,
            )(gql_cls)


convert_module(sensor, "Sensor")
convert_module(control, "Control")

_dedataframed_strawberries = {}


def ensure_dedataframe(annotation):
    if existing := _dedataframed_strawberries.get(annotation, None):
        return existing
    else:
        gql_cls = type(f"{annotation.__name__}SimulationType", (object,), {})
        strawberry.experimental.pydantic.type(
            model=annotation,
            all_fields=True,
            json_schema_directive=JsonSchemaDirective,
            use_pydantic_alias=False,
        )(gql_cls)
        _dedataframed_strawberries[annotation] = gql_cls
        return gql_cls


def ensure_dedataframes(cls):
    for name, field in cls.model_fields.items():
        ensure_dedataframe(field.annotation)


@strawberry.type
class ModuleSimulation[SimulationInput, SimulationOutput]:
    inputs: SimulationInput | None
    outputs: SimulationOutput | None


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
    parameters: Parameters | None
    simulation: ModuleSimulation[SimulationInput, SimulationOutput] | None = None
    automatic: bool | None = None


@dataclass
class ThrsContext(BaseContext):
    messaging: Messaging
    thrusters_messaging: "ThrustersMessaging"
    pvt_messaging: "PvtMessaging"
    pcm_messaging: "PcmMessaging"
    consumers_messaging: "ConsumersMessaging"


type FieldMutation[T] = """Callable[
    [object, object, strawberry.Info[ThrsContext]],
    Coroutine[None, None, T],
]"""

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
    mutation.__name__ = name
    return mutation


def add_control_mutations(
    module: str,
    control_values_cls: type[ThrsModel],
    strawberry_cls: type,
    messaging: Callable[[ThrsContext], MessagingModule],
):
    def _do(cls):
        def _make_control_mutation(name: str, component_type: type):
            async def _mutation(
                self,
                component: component_type,  # type: ignore
                info: strawberry.Info[ThrsContext],
            ) -> strawberry_cls:  # type: ignore
                mod = messaging(info.context)
                control_values = mod.control_values
                if control_values is None:
                    raise Exception("No control values available to modify")
                pydantic_value = component.to_pydantic().to_stamped()
                setattr(control_values, name, pydantic_value)
                expect = mod.wait_for_control_values(
                    lambda v: getattr(v, name) == pydantic_value, timeout=2.0
                )
                await mod.send_manual_controls(control_values)
                await expect
                return strawberry_cls.from_pydantic(control_values)

            return _mutation

        for name, field in control_values_cls.model_fields.items():
            fn = generate_mutation_for_field(
                strawberry_cls,
                f"{module}_control_set_{name}",
                name,
                field,
                _make_control_mutation,
                unstamp=True,
            )
            method = strawberry.mutation(fn)
            setattr(cls, fn.__name__, method)

        return cls

    return _do


def add_parameter_mutations(
    module: str,
    parameters_cls: type[ThrsModel],
    strawberry_cls: type,
    messaging: Callable[[ThrsContext], MessagingModule],
):
    def _do(cls):
        def _make_parameter_mutation(name: str, component_type: type):
            async def _mutation(
                self,
                value: component_type,  # type: ignore
                info: strawberry.Info[ThrsContext],
            ) -> strawberry_cls:  # type: ignore
                mod = messaging(info.context)
                parameters = mod.parameters
                if parameters is None:
                    raise Exception("No parameters available to update")
                setattr(parameters, name, value)
                expect = mod.wait_for_parameters(
                    lambda parameters: getattr(parameters, name) == value, timeout=2
                )
                await mod.set_parameters(parameters)
                await expect
                return strawberry_cls.from_pydantic(parameters)

            return _mutation

        for name, field in parameters_cls.model_fields.items():
            fn = generate_mutation_for_field(
                strawberry_cls,
                f"{module}_parameter_set_{name}",
                name,
                field,
                _make_parameter_mutation,
                unstamp=False,
            )
            method = strawberry.mutation(fn)
            setattr(cls, fn.__name__, method)

        return cls

    return _do


def add_simulation_input_mutations(
    module: str,
    inputs_cls: type[ThrsModel],
    strawberry_cls: type,
    messaging: Callable[[ThrsContext], MessagingModule],
):
    def _do(cls):
        def _make_simulation_input_mutation(name: str, component_type: type):
            async def _mutation(
                self,
                component: component_type,  # type: ignore
                info: strawberry.Info[ThrsContext],
            ) -> strawberry_cls:  # type: ignore
                mod = messaging(info.context)
                inputs = mod.simulation_inputs
                if inputs is None:
                    raise Exception("No simulation inputs available to modify")
                pydantic_value = component.to_pydantic().to_stamped()
                setattr(inputs, name, pydantic_value)

                expect = mod.wait_for_simulation_inputs(
                    lambda inputs: getattr(inputs, name) == pydantic_value,
                    timeout=2,
                )
                await mod.set_simulation_inputs(inputs)
                await expect
                return strawberry_cls.from_pydantic(inputs)

            return _mutation

        for name, field in inputs_cls.model_fields.items():
            fn = generate_mutation_for_field(
                strawberry_cls,
                f"{module}_simulation_set_{name}",
                name,
                field,
                _make_simulation_input_mutation,
                unstamp=True,
            )
            method = strawberry.mutation(fn)
            setattr(cls, fn.__name__, method)

        return cls

    return _do


def add_automation_mode_mutation(
    module: str,
    messaging: Callable[[ThrsContext], MessagingModule],
):
    def _do(cls):
        async def set_automation_mode(
            self,
            automatic: bool,
            info: strawberry.Info[ThrsContext],
        ) -> bool:
            mod = messaging(info.context)
            await mod.set_automation_mode(automatic)
            await mod.wait_for_control_status(automatic, timeout=2)
            return True

        mutation = strawberry.mutation(set_automation_mode)
        setattr(cls, f"{module}_set_automation_mode", mutation)
        return cls

    return _do
