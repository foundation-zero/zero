from dataclasses import dataclass
from datetime import datetime
from functools import reduce
from typing import Generic, Self, TypeVar, get_args

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.fields import FieldInfo

from input_output.units import UnitMeta
from utils.string import hyphenize
import operator


def groupby(iterable, key):
    from itertools import groupby as _groupby

    data = sorted(iterable, key=key)
    return _groupby(data, key)


class ThrsModel(BaseModel):
    """ThrsModel provides the conversion between the dashes in MQTT to Python underscores"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=hyphenize,
        )
    )

    @classmethod
    def zero(cls) -> Self:
        def _zero_component(component):
            return component(
                **{
                    field_name: Stamped.stamp(0)
                    for field_name in component.model_fields.keys()
                }
            )

        vals = {
            component_name: _zero_component(component.annotation)
            for component_name, component in cls.model_fields.items()
        }
        return cls(**vals)

    def values_for_fmu(self) -> dict[str, float]:
        def _values_for_component(component_name, component):
            def _name_for_field(field_name, field: FieldInfo):
                unit = next(iter(field.annotation.__pydantic_generic_metadata__["args"]), None)  # type: ignore
                unit_meta = (
                    next(
                        (
                            meta
                            for meta in get_args(unit.__value__)
                            if isinstance(meta, UnitMeta)
                        ),
                        None,
                    )
                    if unit and hasattr(unit, "__value__")
                    else None
                )
                if unit_meta:
                    return f"{component_name}__{field_name}__{unit_meta.modelica_name}"
                else:
                    return f"{component_name}__{field_name}"

            return {
                _name_for_field(field_name, field): getattr(component, field_name).value
                for field_name, field in component.model_fields.items()
            }

        vals = [
            _values_for_component(component_name, getattr(self, component_name))
            for component_name in self.model_fields.keys()
        ]
        return reduce(operator.ior, vals, {})

    @classmethod
    def build_from_fmu(cls, values: dict[str, float]) -> Self:
        # first part is the component name, second part is the field name, third (if any) is the unit
        # ignore third, build dict of dict of first part and second part
        def _split_component_field(key: str):
            component, field, *_ = key.split("__")
            return component, field

        split_values = [
            (*_split_component_field(key), value) for key, value in values.items()
        ]
        grouped_by_component = groupby(split_values, key=operator.itemgetter(0))
        nested_values = {
            component: {field: Stamped.stamp(value) for _, field, value in field_values}
            for component, field_values in grouped_by_component
        }
        return cls.model_validate(nested_values)


T = TypeVar("T")


class Stamped(ThrsModel, Generic[T]):
    value: T
    timestamp: datetime

    @staticmethod
    def stamp[V](value: V) -> "Stamped[V]":
        return Stamped(value=value, timestamp=datetime.now())


@dataclass
class Meta:
    yard_tag: str
