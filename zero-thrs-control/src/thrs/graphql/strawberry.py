from typing import Annotated, Callable, Generic, TypeVar, get_args
from pydantic import Field, create_model
from strawberry.schema_directive import Location
import strawberry
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
)
import thrs.input_output.definitions.sensor as sensor
import thrs.input_output.definitions.control as control
from thrs.input_output.base import Stamped, ThrsModel
from pydantic.fields import FieldInfo


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


@strawberry.experimental.pydantic.type(
    model=sensor.TemperatureSensor,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class TemperatureSensorType:
    pass


@strawberry.experimental.pydantic.type(
    model=sensor.Valve, all_fields=True, json_schema_directive=JsonSchemaDirective
)
class SensorValveType:
    pass


@strawberry.experimental.pydantic.type(
    model=sensor.FlowSensor, all_fields=True, json_schema_directive=JsonSchemaDirective
)
class SensorFlowType:
    pass


@strawberry.experimental.pydantic.type(
    model=sensor.PressureSensor,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class SensorPressureType:
    pass


@strawberry.experimental.pydantic.type(
    model=sensor.Thruster, all_fields=True, json_schema_directive=JsonSchemaDirective
)
class SensorThrusterType:
    pass


@strawberry.experimental.pydantic.type(
    model=sensor.Pcs, all_fields=True, json_schema_directive=JsonSchemaDirective
)
class SensorPcsType:
    pass


@strawberry.experimental.pydantic.type(
    model=sensor.Pump, all_fields=True, json_schema_directive=JsonSchemaDirective
)
class SensorPumpType:
    pass


@strawberry.experimental.pydantic.type(
    model=control.Pump, all_fields=True, json_schema_directive=JsonSchemaDirective
)
class ControlPumpType:
    pass


@strawberry.experimental.pydantic.type(
    model=control.Valve, all_fields=True, json_schema_directive=JsonSchemaDirective
)
class ControlValveType:
    pass


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


SensorValues = TypeVar("SensorValues")
ControlValues = TypeVar("ControlValues")


@strawberry.type
class Module(Generic[SensorValues, ControlValues]):
    sensor_values: SensorValues
    control_values: ControlValues


@strawberry.type
class Modules:
    thrusters: Module[ThrustersSensorValuesType, ThrustersControlValuesType]


thrusters_control_values = ThrustersControlValues.zero()


@strawberry.type
class Query:
    @strawberry.field()
    def modules(
        self,
    ) -> Modules:
        return Modules(
            thrusters=Module(
                sensor_values=ThrustersSensorValuesType.from_pydantic(
                    ThrustersSensorValues.zero()
                ),
                control_values=ThrustersControlValuesType.from_pydantic(
                    thrusters_control_values
                ),
            ),
        )

    @strawberry.field()
    def thrusters_sensor_values(self) -> ThrustersSensorValuesType:
        return ThrustersSensorValuesType.from_pydantic(ThrustersSensorValues.zero())


_input_types = {}


class UnstampedInput(ThrsModel):
    @staticmethod
    def generate_for_model(name: str, model: type[ThrsModel]):
        fields = {
            key: Annotated[
                get_args(field.annotation.__pydantic_generic_metadata__["args"][0])[0],  # type: ignore
                Field(),
            ]
            for key, field in model.model_fields.items()
            if field.annotation.__pydantic_generic_metadata__["origin"]  # type: ignore
            is Stamped
        }
        unstamped_model = create_model(name, **fields, __base__=UnstampedInput)  # type: ignore
        unstamped_model._MODEL = model
        return unstamped_model

    def to_stamped(self):
        values = {
            key: Stamped.stamp(getattr(self, key)) for key in self.model_fields.keys()
        }
        return self._MODEL(**values)  # type: ignore


def ensure_input_type(annotation):
    if existing := _input_types.get(annotation.__name__, None):
        return existing
    else:
        input_model = UnstampedInput.generate_for_model(
            f"{annotation.__name__}InputType", annotation
        )
        input_type = strawberry.experimental.pydantic.input(
            model=input_model, all_fields=True
        )(type(f"{annotation.__name__}InputType", (object,), {}))
        _input_types[annotation.__name__] = input_type
        return input_type


def generate_mutation_for_field(
    name: str, field: FieldInfo
) -> "Callable[[Mutation, object], ThrustersControlValuesType]":
    input_type = ensure_input_type(field.annotation)

    def _mutation(self, component: input_type) -> ThrustersControlValuesType:  # type: ignore
        pydantic_value = component.to_pydantic().to_stamped()
        setattr(thrusters_control_values, name, pydantic_value)
        return ThrustersControlValuesType.from_pydantic(thrusters_control_values)

    _mutation.__name__ = f"set_{name}"
    return _mutation


class DynamicInputFields:
    def __init_subclass__(cls):
        for name, field in ThrustersControlValues.model_fields.items():
            fn = generate_mutation_for_field(name, field)
            method = strawberry.mutation(fn)
            setattr(cls, fn.__name__, method)


@strawberry.type
class Mutation(DynamicInputFields):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
