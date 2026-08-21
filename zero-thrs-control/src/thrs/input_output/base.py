from dataclasses import dataclass
from datetime import UTC, datetime
from inspect import isclass
from typing import Annotated, Any, Literal, NamedTuple, Self, cast, get_args, get_origin

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


class Payload:
    """Marker mixin: a ThrsValues subclass whose fields are serialised as a single JSON payload
    on its own MQTT topic rather than being further expanded into sub-topics."""


class FieldLeaf(NamedTuple):
    """A resolved leaf in the topic tree produced by :func:`walk_fields`."""

    topic: str
    """Full MQTT topic for this leaf (no wildcards)."""
    field_path: tuple[str, ...]
    """Sequence of attribute names to reach the value from the root model."""
    annotation: type
    """Concrete Python type of the leaf value (a ThrsValues+Payload subclass or a scalar)."""
    is_payload: bool
    """True when *annotation* inherits from both ThrsValues and Payload."""


def _bare_type(annotation: Any) -> Any:
    """Strip a single level of Annotated[T, ...] and return the bare type."""
    if get_origin(annotation) is Annotated:
        return get_args(annotation)[0]
    return annotation


def walk_fields(
    cls: type[ThrsValues],
    base_topic: str,
    *,
    _field_path: tuple[str, ...] = (),
) -> list[FieldLeaf]:
    """Recursively walk all fields of a :class:`ThrsValues` subclass and return a flat list of
    :class:`FieldLeaf` entries, one per MQTT topic leaf.

    The walk follows these rules for each field:

    * If the bare annotation is a subclass of both :class:`ThrsValues` **and** :class:`Payload`,
      the field is a **payload leaf** — its full model is expected as a JSON payload on a single
      topic and is not expanded further.
    * If the bare annotation is a subclass of :class:`ThrsValues` **only**, the field is a
      **path component** — ``field_name`` (or a ``topic_override``) is appended to the topic
      and the walk recurses into that nested model.
    * Otherwise the field is a **scalar leaf** — its raw value lives on the derived topic.

    Topic segments are derived from ``field_name`` with underscores replaced by hyphens unless
    a ``topic_override`` is present in the field's :class:`ComponentMeta`.

    Args:
        cls: The root :class:`ThrsValues` subclass to inspect.
        base_topic: MQTT topic prefix for this level of the tree (e.g. ``"vessel/module"``).

    Returns:
        A flat list of :class:`FieldLeaf` instances in field-declaration order.
    """
    leaves: list[FieldLeaf] = []

    for field_name, field_info in cls.model_fields.items():
        bare = _bare_type(field_info.annotation)

        topic_override = get_topic(field_info)
        segment = topic_override if topic_override else field_name.replace("_", "-")
        topic = f"{base_topic}/{segment}"

        path = _field_path + (field_name,)

        if isclass(bare) and issubclass(bare, ThrsValues):
            if issubclass(bare, Payload):
                # Payload leaf: entire sub-model serialised as one JSON blob
                leaves.append(FieldLeaf(topic=topic, field_path=path, annotation=bare, is_payload=True))
            else:
                # Path component: recurse into the nested ThrsValues
                leaves.extend(walk_fields(bare, topic, _field_path=path))
        else:
            # Scalar leaf
            leaves.append(FieldLeaf(topic=topic, field_path=path, annotation=bare, is_payload=False))

    return leaves
