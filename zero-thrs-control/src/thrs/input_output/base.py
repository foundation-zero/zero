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
                unit = unit_for_annotation(field.annotation)
                return zero_for_unit(unit) if unit else 0.0

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


class ComponentMeta(BaseModel):
    yard_tag: str = ""
    included_in_fmu: bool = True
    component_type: str | None = None
    valve_type: Literal["shutoff", "switch", "mix", "flowcontrol"] | None = None
    topic_override: str | None = None


def computed_meta(**kwargs):
    return ComponentMeta(**kwargs).model_dump()


def component_meta(**kwargs):
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


def field_meta(*args, **kwargs):
    return Field(json_schema_extra=FieldMeta(*args, **kwargs).model_dump())


@dataclass
class CombinedValues:
    values: dict[str, ThrsValues]
