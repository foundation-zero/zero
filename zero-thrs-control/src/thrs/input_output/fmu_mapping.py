import operator
from datetime import datetime
from typing import Any, overload

from pydantic.fields import FieldInfo, ComputedFieldInfo

from thrs.input_output.base import Stamped, ThrsModel


def groupby(iterable, key):
    from itertools import groupby as _groupby

    data = sorted(iterable, key=key)
    return _groupby(data, key)


def included_in_fmu(field: FieldInfo | ComputedFieldInfo) -> bool:
    """Check if the field should be included in the FMU."""
    return (
        field.json_schema_extra.get("included_in_fmu", True)
        if field.json_schema_extra and isinstance(field.json_schema_extra, dict)
        else True
    )  # type: ignore


def extract_non_fmu_values(
    simulation_input: ThrsModel, sensor_cls: type[ThrsModel]
) -> dict[str, dict[str, Stamped[Any]]]:
    """Extract values that are not included in the FMU."""

    def _lookup_values(simulation_value: ThrsModel, sensor_component_field: FieldInfo):
        return {
            name: getattr(simulation_value, name)
            for name in sensor_component_field.annotation.model_fields.keys()  # type: ignore
        }

    return {
        component_name: _lookup_values(getattr(simulation_input, component_name), field)
        for component_name, field in sensor_cls.model_fields.items()
        if not included_in_fmu(field)
    }


@overload
def build_outputs_from_fmu[T: ThrsModel](
    clss: tuple[type[T]],
    values: dict[str, float],
    timestamp: datetime,
    extra_values: dict[str, dict[str, Stamped[Any]]] = {},
) -> tuple[T]: ...


@overload
def build_outputs_from_fmu[T: ThrsModel, T2: ThrsModel](
    clss: tuple[type[T], type[T2]],
    values: dict[str, float],
    timestamp: datetime,
    extra_values: dict[str, dict[str, Stamped[Any]]] = {},
) -> tuple[T, T2]: ...


def build_outputs_from_fmu(
    clss: tuple[type[ThrsModel], ...],
    values: dict[str, float],
    timestamp: datetime,
    extra_values: dict[str, dict[str, Stamped[Any]]] = {},
) -> tuple[ThrsModel, ...]:
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
        component: extra_values.get(component, {})
        | {
            field: Stamped(value=value, timestamp=timestamp)
            for _, field, value in field_values
        }
        for component, field_values in grouped_by_component
    }
    unused_extra_values = {
        component_name: component
        for component_name, component in extra_values.items()
        if component_name not in nested_values
    }
    with_extras = nested_values | unused_extra_values

    return tuple([cls(**with_extras) for cls in clss])
