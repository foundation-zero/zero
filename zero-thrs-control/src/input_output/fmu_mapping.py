import operator
from datetime import datetime
from functools import reduce
from typing import Any

from pydantic.fields import FieldInfo

from input_output.base import Stamped, ThrsModel
from input_output.definitions.units import unit_for_annotation, unit_meta


def groupby(iterable, key):
    from itertools import groupby as _groupby

    data = sorted(iterable, key=key)
    return _groupby(data, key)


def included_in_fmu(field: FieldInfo) -> bool:
    """Check if the field should be included in the FMU."""
    meta = next((meta for meta in field.metadata if hasattr(meta, "included_in_fmu")), None)
    return meta.included_in_fmu if meta else True


def build_inputs_for_fmu(
    model: ThrsModel,
) -> dict[str, float]:
    def _values_for_component(component_name, component):
        def _name_for_field(field_name, field: FieldInfo):
            meta = unit_meta(unit_for_annotation(field.annotation))  # type: ignore
            if meta:
                return f"{component_name}__{field_name}__{meta.modelica_name}"
            else:
                return f"{component_name}__{field_name}"

        return {
            _name_for_field(field_name, field): getattr(component, field_name).value
            for field_name, field in component.model_fields.items()
            if included_in_fmu(field)
        }

    vals = [
        _values_for_component(component_name, getattr(model, component_name))
        for component_name, field in model.model_fields.items()
        if included_in_fmu(field)
    ]
    return reduce(operator.ior, vals, {})


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


def build_outputs_from_fmu(
    clss: list[type[ThrsModel]],
    values: dict[str, float],
    timestamp: datetime,
    extra_values: dict[str, dict[str, Stamped[Any]]] = {},
) -> list[ThrsModel]:
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
        component: extra_values.get(component, {}) | {
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

    return [cls(**with_extras) for cls in clss]
