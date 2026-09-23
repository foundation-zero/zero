from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated, Any, Literal, Self, cast

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal
from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.input_output.definitions.units import (
    unit_for_annotation,
    zero_for_unit,
)


class ThrsValues(BaseModel):
    """ThrsValues provides the conversion between the camel case in MQTT messages to Python underscores"""

    model_config = ConfigDict(
        alias_generator=to_pascal,
        use_enum_values=True,
        validate_by_name=True,
        validate_assignment=True,
    )

    @classmethod
    def zero(cls) -> Self:
        def _zero_component(component):
            def _zero_value(field: FieldInfo):
                if isinstance(field.json_schema_extra, dict):
                    override = field.json_schema_extra.get("zero_value")
                    if override is not None:
                        return override
                unit = unit_for_annotation(field.annotation)
                if unit is datetime:
                    return datetime.fromtimestamp(0, UTC)
                return zero_for_unit(unit) if unit else 0.0

            if issubclass(component, Stamped):
                return Stamped.stamp(zero_for_unit(unit_for_annotation(component)))
            if issubclass(component, ThrsValues):
                return component(
                    **{
                        field_name: Stamped.stamp(_zero_value(field))
                        for field_name, field in component.model_fields.items()
                    }
                )
            unit = unit_for_annotation(component)
            return zero_for_unit(unit) if unit else 0.0

        vals = {
            component_name: _zero_component(component.annotation)
            for component_name, component in cls.model_fields.items()
        }
        return cls(**vals)

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


class Stamped[T](ThrsValues):
    value: T
    timestamp: Annotated[datetime, Field(alias="TimeStamp")]

    @staticmethod
    def stamp[V](value: V) -> "Stamped[V]":
        return Stamped(value=value, timestamp=datetime.now(UTC))

    @staticmethod
    def combine[V](*stamped: "Stamped[Any]", value: V) -> "Stamped[V]":
        return Stamped(value=value, timestamp=min(s.timestamp for s in stamped))


class StampedWithSource[T](Stamped[T]):
    source: str

    @staticmethod
    def stamp[V](value: V, source: str) -> "StampedWithSource[V]":  # type: ignore
        return StampedWithSource(
            value=value, timestamp=datetime.now(UTC), source=source
        )

    @staticmethod
    def from_stamped[V](original: Stamped[V], source: str) -> "StampedWithSource[V]":
        return StampedWithSource(
            value=original.value, timestamp=original.timestamp, source=source
        )

    @staticmethod
    def combine[V](  # type: ignore
        *stamped: "Stamped[Any]", value: V, source: str
    ) -> "StampedWithSource[V]":
        return StampedWithSource(
            value=value, timestamp=min(s.timestamp for s in stamped), source=source
        )


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
    "pcm_input",
    "pcm",
    "pcs",
    "power_sensor",
    "pressure_sensor",
    "propulsion_drive",
    "pump",
    "shore_power_converter",
    "temperature_sensor",
    "thruster",
    "ugrid",
    "tank_controller",
    "pid_controller",
]
type SpecialComponentType = Literal["valve"]


class BaseMeta(BaseModel):
    component_type: BaseComponentType | None = None
    yard_tag: str = ""
    included_in_fmu: bool = True
    topic_override: str | None = None


class ValveMeta(BaseMeta):
    component_type: Literal["valve"]  # type: ignore
    valve_type: Literal["shutoff", "switch", "mix", "flowcontrol"] | None = None


class ComponentMeta(ValveMeta):
    component_type: BaseComponentType | SpecialComponentType | None = None  # type: ignore


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

    return field.json_schema_extra.get("topic_override")  # type: ignore


@dataclass
class ParameterMeta:
    fds_tag: str


class FieldMeta(BaseModel):
    included_in_fmu: bool = True
    zero_value: Any | None = None


def field_meta(*args, **kwargs):
    return Field(
        json_schema_extra=FieldMeta(*args, **kwargs).model_dump(exclude_none=True)
    )


@dataclass
class CombinedValues:
    values: dict[str, ThrsValues]
