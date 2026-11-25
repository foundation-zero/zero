from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated, Any, Literal, Self, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator
from pydantic.alias_generators import to_pascal
from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.input_output.definitions.units import (
    unit_for_annotation,
    zero_for_unit,
)
from thrs.input_output.definitions.wire_context import is_set


class ThrsValues(BaseModel):
    """ThrsValues provides the conversion between the camel case in MQTT messages to Python underscores"""

    model_config = ConfigDict(
        alias_generator=to_pascal,
        use_enum_values=True,
        validate_by_name=True,
        validate_assignment=True,
    )

    @classmethod
    def initial(cls, timestamp: datetime | None = None) -> Self:
        """Every component at its initial value, stamped at `timestamp`, or now."""
        stamped_at = timestamp or datetime.now(UTC)
        return cls(
            **{
                name: initial_field(field, stamped_at)
                for name, field in cls.model_fields.items()
            }
        )

    def update_in_place(self, other: Self) -> None:
        """Copy the values of other into self, keeping the identity of nested components."""
        for field_name in type(self).model_fields:
            current = getattr(self, field_name)
            incoming = getattr(other, field_name)

            if isinstance(current, Stamped):
                setattr(self, field_name, incoming.model_copy(deep=True))
            elif isinstance(current, ThrsValues):
                current.update_in_place(incoming)
            elif isinstance(current, list):
                for idx, (current_item, incoming_item) in enumerate(
                    zip(current, incoming, strict=True)
                ):
                    if isinstance(current_item, ThrsValues):
                        current_item.update_in_place(incoming_item)
                    elif isinstance(current_item, Stamped):
                        current[idx] = incoming_item.model_copy(deep=True)
                    else:
                        current[idx] = incoming_item
            else:
                setattr(self, field_name, incoming)

    @classmethod
    def yard_tag(cls, field_name: str) -> str:
        return cast(dict, cls.model_fields[field_name].json_schema_extra)["yard_tag"]


def _stamped_schema(schema: dict[str, Any]) -> None:
    """A stamped value's JSON Schema, as the Spec describes it:

    - `TimeStamp` is not required, as a client's write may leave it out (see
      `Stamped._stamp_on_arrival`);
    - a number `Value`, nullable or not, has `format: float`: the AMCS keeps its
      values as float32, so a client compares what it wrote with what comes back
      at that precision. Tuples of numbers stay plain: they are controller state,
      which no client writes.
    """
    schema["required"] = [name for name in schema["required"] if name != "TimeStamp"]
    value = schema["properties"]["Value"]
    for number in [value, *value.get("anyOf", [])]:
        if number.get("type") == "number":
            number["format"] = "float"


class Stamped[T](ThrsValues):
    model_config = ConfigDict(json_schema_extra=_stamped_schema)

    value: T
    timestamp: Annotated[datetime, Field(alias="TimeStamp")]

    @model_validator(mode="before")
    @classmethod
    def _stamp_on_arrival(cls, data: Any, info: ValidationInfo) -> Any:
        """A client's write without a `TimeStamp` is stamped when it arrives;
        everywhere else a value must carry its own."""
        if (
            is_set(info.context)
            and isinstance(data, dict)
            and "TimeStamp" not in data
            and "timestamp" not in data
        ):
            return {**data, "TimeStamp": datetime.now(UTC)}
        return data

    @staticmethod
    def stamp[V](value: V) -> Stamped[V]:
        return Stamped(value=value, timestamp=datetime.now(UTC))

    @staticmethod
    def combine[V](*stamped: Stamped[Any], value: V) -> Stamped[V]:
        return Stamped(value=value, timestamp=min(s.timestamp for s in stamped))


class StampedWithSource[T](Stamped[T]):
    source: str

    @staticmethod
    def stamp[V](value: V, source: str) -> StampedWithSource[V]:  # pyrefly: ignore[bad-override]
        return StampedWithSource(
            value=value, timestamp=datetime.now(UTC), source=source
        )

    @staticmethod
    def from_stamped[V](original: Stamped[V], source: str) -> StampedWithSource[V]:
        if isinstance(original, StampedWithSource):
            return original

        return StampedWithSource(
            value=original.value, timestamp=original.timestamp, source=source
        )

    @staticmethod
    def combine[V](  # pyrefly: ignore[bad-override]
        *stamped: Stamped[Any], value: V, source: str
    ) -> StampedWithSource[V]:
        return StampedWithSource(
            value=value, timestamp=min(s.timestamp for s in stamped), source=source
        )


def initial_component(component: Any, stamped_at: datetime) -> Any:
    """A component at its initial value, its own components through their fields."""
    if isinstance(component, type):
        if issubclass(component, StampedWithSource):
            return StampedWithSource(
                value=zero_for_unit(unit_for_annotation(component)),
                timestamp=stamped_at,
                source="initialization",
            )
        if issubclass(component, Stamped):
            return Stamped(
                value=zero_for_unit(unit_for_annotation(component)),
                timestamp=stamped_at,
            )
        if issubclass(component, ThrsValues):
            return component(
                **{
                    field_name: initial_field(field, stamped_at)
                    for field_name, field in component.model_fields.items()
                }
            )
    return zero_for_unit(unit_for_annotation(component))


def initial_field(field: FieldInfo, stamped_at: datetime) -> Any:
    """A field at its initial value: its `initial_value` override, stamped, else the
    initial value of its component."""
    if isinstance(field.json_schema_extra, dict):
        override = field.json_schema_extra.get("initial_value")
        if override is not None:
            return Stamped(value=override, timestamp=stamped_at)
    return initial_component(field.annotation, stamped_at)


def _factory[R, **P](
    cls: Callable[P, Any],
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func):
        return func

    return inner


# If you add something here, make sure this type is also handled in the script that generate typescript for the frontend
type BaseComponentType = Literal[
    "adsorption_chiller",
    "brightloop",
    "brightloop_converter",
    "brightloop_group",
    "calculated_flow",
    "calculated_temperature",
    "delta_t",
    "external_sensor",
    "flow_sensor",
    "heat_transfer",
    "heatpump",
    "hvac_exchanger",
    "level_sensor",
    "level_switch",
    "pcm",
    "pcs",
    "power_sensor",
    "pressure_sensor",
    "propulsion_drive",
    "pump",
    "shore_power_converter",
    "shore_power_group",
    "temperature_sensor",
    "thruster",
    "ugrid",
    "ugrid_group",
    "tank_controller",
    "pid_controller",
    "pcm_charge_controller",
    "controller_state",
    "pvt",
    "pyranometer",
]
type SpecialComponentType = Literal["valve"]
type ComponentType = BaseComponentType | SpecialComponentType | None


class BaseMeta(BaseModel):
    component_type: BaseComponentType | None = None
    yard_tag: str = ""
    included_in_fmu: bool = True
    topic_override: str | None = None


class ValveMeta(BaseMeta):
    component_type: Literal["valve"]  # pyrefly: ignore[bad-override]
    valve_type: Literal["shutoff", "switch", "mix", "flowcontrol"] | None = None


class ComponentMeta(ValveMeta):
    component_type: ComponentType = None  # pyrefly: ignore[bad-override]


@_factory(BaseMeta)
def computed_meta(**kwargs):
    return ComponentMeta(**kwargs).model_dump()


@_factory(BaseMeta)
def component_meta(**kwargs):
    return Field(json_schema_extra=computed_meta(**kwargs))


@_factory(ValveMeta)
def valve_meta(**kwargs):
    return Field(json_schema_extra=computed_meta(**kwargs))


def get_topic(field: FieldInfo | ComputedFieldInfo) -> str | None:
    if not field.json_schema_extra or not isinstance(field.json_schema_extra, dict):
        return None

    return field.json_schema_extra.get("topic_override")  # pyrefly: ignore[bad-return]


def get_component_type(
    field: FieldInfo | ComputedFieldInfo,
) -> ComponentType:
    if not field.json_schema_extra or not isinstance(field.json_schema_extra, dict):
        return None

    return field.json_schema_extra.get("component_type")  # pyrefly: ignore[bad-return]


def get_yard_tag(field: FieldInfo | ComputedFieldInfo) -> str | None:
    if not field.json_schema_extra or not isinstance(field.json_schema_extra, dict):
        return None

    # BaseMeta defaults the yard tag to "", which means it has none.
    return field.json_schema_extra.get("yard_tag") or None  # pyrefly: ignore[bad-return]


@dataclass
class ParameterMeta:
    fds_tag: str


class FieldMeta(BaseModel):
    included_in_fmu: bool = True
    initial_value: Any | None = None


def field_meta(*args, **kwargs):
    return Field(
        json_schema_extra=FieldMeta(*args, **kwargs).model_dump(exclude_none=True)
    )


@dataclass
class CombinedValues:
    values: dict[str, ThrsValues]
