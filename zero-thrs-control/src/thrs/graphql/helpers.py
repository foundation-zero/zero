from typing import Annotated, get_args, get_origin

import strawberry
from pydantic import BaseModel, Field, create_model
from strawberry.schema_directive import Location

from thrs.input_output.base import SimulationValues, Stamped, ThrsValues
from thrs.input_output.definitions.units import unit_for_annotation


@strawberry.schema_directive(locations=[Location.FIELD_DEFINITION])
class JsonSchemaDirective:
    yard_tag: str | None = None
    component_type: str | None = None
    valve_type: str | None = None


_dedataframed_strawberries = {}


def ensure_dedataframe(annotation):
    """
    Ensure a Pydantic model is converted to a Strawberry type for simulation data.

    This function caches converted types to avoid duplicate conversions.
    """
    if existing := _dedataframed_strawberries.get(annotation):
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
    """
    Ensure all fields in a Pydantic model are converted to Strawberry types.

    This is used for simulation input/output types that may contain complex nested types.
    """
    for name, field in cls.model_fields.items():
        ensure_dedataframe(field.annotation)


def pydantic_to_strawberry_type(
    pydantic_model: type[BaseModel],
    suffix: str = "Type",
    include_computed: bool = False,
) -> type:
    """
    Convert a Pydantic model to a Strawberry GraphQL type.

    Args:
        pydantic_model: The Pydantic model class to convert
        suffix: Suffix to add to the type name (default: "Type")
        include_computed: Whether to include computed fields (default: False)

    Returns:
        A Strawberry GraphQL type class

    Example:
        Instead of:
            @strawberry.experimental.pydantic.type(
                model=ThrustersSensorValues,
                all_fields=True,
                json_schema_directive=JsonSchemaDirective,
                use_pydantic_alias=False,
            )
            class ThrustersSensorValuesType:
                pass

        Use:
            ThrustersSensorValuesType = pydantic_to_strawberry_type(ThrustersSensorValues)
    """
    type_name = f"{pydantic_model.__name__}{suffix}"
    graphql_class = type(type_name, (object,), {})
    return strawberry.experimental.pydantic.type(
        model=pydantic_model,
        all_fields=True,
        include_computed=include_computed,
        json_schema_directive=JsonSchemaDirective,
        use_pydantic_alias=False,
    )(graphql_class)


def optional_pydantic_to_graphql(graphql_type: type, pydantic_value):
    """
    Convert a Pydantic value to Strawberry GraphQL type if the value exists.

    This simplifies resolver functions by handling the None-checking pattern.

    Args:
        graphql_type: The Strawberry GraphQL type class
        pydantic_value: The Pydantic model instance (or None)

    Returns:
        Converted GraphQL type instance, or None if pydantic_value was None

    Example:
        Instead of:
            sensor_values=(
                ThrustersSensorValuesType.from_pydantic(module.sensor_values)
                if module.sensor_values
                else None
            )

        Use:
            sensor_values=optional_convert(ThrustersSensorValuesType, module.sensor_values)
    """
    if pydantic_value is None:
        return None
    return graphql_type.from_pydantic(pydantic_value)


def dedataframed_pydantic_to_strawberry_type(cls: type[SimulationValues]) -> type:
    """
    Create a Strawberry GraphQL type for a simulation values class.

    Handles the dedataframe boilerplate automatically. This converts simulation
    models that may contain time-series DataFrames (StampedDf[T]) into GraphQL-
    compatible types with only scalar values (Stamped[T]).

    Args:
        cls: The simulation Pydantic model (inputs or outputs)

    Returns:
        Strawberry GraphQL type

    Example:
        Instead of:
            DedataframedInputs = ThrustersSimulationInputs.dedataframe()
            ensure_dedataframes(DedataframedInputs)

            @strawberry.experimental.pydantic.type(...)
            class ThrustersSimulationInputsType:
                pass

        Use:
            ThrustersSimInputsType = create_simulation_type(ThrustersSimulationInputs)
            ThrustersSimOutputsType = create_simulation_type(ThrustersSimulationOutputs)
    """
    # Dedataframe: convert StampedDf[T] fields to Stamped[T]
    dedataframed = cls.dedataframe()

    # Ensure all nested component fields are converted to Strawberry types
    ensure_dedataframes(dedataframed)

    # Create final Strawberry GraphQL type
    return pydantic_to_strawberry_type(dedataframed)


class UnstampedInput(ThrsValues):
    """
    Base class for unstamped input types used in GraphQL mutations.

    The THRS system internally uses Stamped[T] values (value + timestamp) for
    all sensor readings and control values to support time-series analysis.

    However, GraphQL mutation inputs should accept simple values without timestamps.
    The server automatically adds timestamps when the mutation is received.

    This class provides a dynamic model generator that:
    1. Takes a model with Stamped[T] fields
    2. Generates a new model with just the raw value types
    3. Provides a to_stamped() method to add timestamps automatically

    Example:
        Original model:
            class PumpControl(ThrsValues):
                dutypoint: Stamped[Ratio]
                on: Stamped[bool]

        Generated unstamped input:
            class PumpControlInput(UnstampedInput):
                dutypoint: float  # Ratio's underlying type
                on: bool

        Usage in mutation:
            input = PumpControlInput(dutypoint=0.5, on=True)
            stamped = input.to_stamped()
            # Result: PumpControl(
            #   dutypoint=Stamped(value=0.5, timestamp=now),
            #   on=Stamped(value=True, timestamp=now)
            # )
    """

    @staticmethod
    def generate_for_model(name: str, model: type[ThrsValues]):
        """
        Generate an unstamped input model from a stamped model.

        Args:
            name: Name for the generated model class
            model: The stamped model to generate an input type from

        Returns:
            A new Pydantic model class with unstamped fields
        """

        def _unstamped_type(unit):
            return get_args(unit)[0] if get_origin(unit) is Annotated else unit

        fields = {
            key: Annotated[
                _unstamped_type(unit),
                Field(),
            ]
            for key, field in model.model_fields.items()
            if (unit := unit_for_annotation(field.annotation))
        }
        unstamped_model = create_model(name, **fields, __base__=UnstampedInput)  # type: ignore
        unstamped_model._MODEL = model  # type: ignore
        return unstamped_model

    def to_stamped(self):
        """
        Convert unstamped input values to stamped values with current timestamp.

        Returns:
            Instance of the original stamped model with timestamps added
        """
        values = {
            key: Stamped.stamp(getattr(self, key)) for key in type(self).model_fields
        }
        return self._MODEL(**values)  # type: ignore


_input_types = {}


def ensure_input_type(annotation, unstamp: bool) -> type:
    """
    Ensure a GraphQL input type exists for the given annotation.

    This is used by mutation decorators to generate input types on demand.
    Results are cached to avoid regenerating the same type multiple times.

    Args:
        annotation: The field annotation (e.g. Stamped[Celsius])
        unstamp: Whether to generate an unstamped input type

    Returns:
        A Strawberry input type class
    """
    if existing := _input_types.get(annotation.__name__):
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
