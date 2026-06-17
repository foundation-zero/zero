import operator
from datetime import datetime
from typing import Any, overload

from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.input_output.base import (
    SimulationValues,
    Stamped,
    ThrsValues,
)
from thrs.input_output.definitions.units import unit_for_annotation, unit_meta


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


def _fmu_key_for_field(
    component_name: str, field_name: str, field: FieldInfo | ComputedFieldInfo
) -> str:
    annotation = (
        field.json_schema_extra if isinstance(field, ComputedFieldInfo) else field.annotation
    )
    meta = unit_meta(unit_for_annotation(annotation))  # type: ignore
    if meta:
        return f"{component_name}__{field_name}__{meta.modelica_name}"
    return f"{component_name}__{field_name}"


def build_fmu_key_mapping(
    cls: type[ThrsValues], fmu_only: bool = True
) -> dict[tuple[str, str], str]:
    """Return a dict mapping a (component_name, field_name) tuple to a Modelica name str for a ThrsValues model."""

    component_classes = [
        (
            component_name,
            component.annotation
            if isinstance(component, FieldInfo)
            else component.json_schema_extra,
        )
        for component_name, component in {
            **cls.model_fields,
            **cls.model_computed_fields,
        }.items()
        if fmu_only is False or included_in_fmu(component)
    ]

    component_fields = [
        (component_name, field_name, field)
        for component_name, component_cls in component_classes
        for field_name, field in {
            **component_cls.model_fields,  # type: ignore
            **component_cls.model_computed_fields,  # type: ignore
        }.items()
        if fmu_only is False or included_in_fmu(field)
    ]

    mapping = {
        (component_name, field_name): _fmu_key_for_field(
            component_name, field_name, field
        )
        for component_name, field_name, field in component_fields
    }

    return mapping


def extract_non_fmu_values(
    simulation_values: SimulationValues, sensor_cls: type[ThrsValues]
) -> dict[str, dict[str, Stamped[Any]]]:
    """Extract values from simulation values that are not included in the FMU."""

    def _lookup_values(
        simulation_input: ThrsValues,
        sensor_component_field: FieldInfo | ComputedFieldInfo,
    ):
        # If the whole component is excluded from FMU, extract all available fields
        if not included_in_fmu(sensor_component_field):
            return {
                name: getattr(simulation_input, name)
                for name in type(simulation_input).model_fields
            }
        # Otherwise, only return fields that are excluded
        component_type = (
            sensor_component_field.json_schema_extra
            if isinstance(sensor_component_field, ComputedFieldInfo)
            else sensor_component_field.annotation
        )
        return {
            name: getattr(simulation_input, name)
            for name, field in component_type.model_fields.items()  # type: ignore
            if not included_in_fmu(field)
        }

    all_sensor_fields: dict[str, FieldInfo | ComputedFieldInfo] = {
        **sensor_cls.model_fields,
        **sensor_cls.model_computed_fields,
    }

    return {
        component_name: values
        for component_name, field in all_sensor_fields.items()
        if hasattr(simulation_values, component_name)
        and (
            values := _lookup_values(getattr(simulation_values, component_name), field)
        )
    }


@overload
def build_outputs_from_fmu[T: ThrsValues](
    clss: tuple[type[T]],
    values: dict[str, float],
    timestamp: datetime,
    non_fmu_simulation_inputs: dict[str, dict[str, Stamped[Any]]] = {},
) -> tuple[T]: ...


@overload
def build_outputs_from_fmu[T: ThrsValues, T2: ThrsValues](
    clss: tuple[type[T], type[T2]],
    values: dict[str, float],
    timestamp: datetime,
    non_fmu_simulation_inputs: dict[str, dict[str, Stamped[Any]]] = {},
) -> tuple[T, T2]: ...


@overload
def build_outputs_from_fmu[T: ThrsValues](
    clss: tuple[type[T], ...],
    values: dict[str, float],
    timestamp: datetime,
    non_fmu_simulation_inputs: dict[str, dict[str, Stamped[Any]]] = {},
) -> tuple[T, ...]: ...


def build_outputs_from_fmu(
    clss: tuple[type[ThrsValues], ...],
    values: dict[str, float],
    timestamp: datetime,
    non_fmu_simulation_inputs: dict[str, dict[str, Stamped[Any]]] = {},
) -> tuple[ThrsValues, ...]:
    # first part is the component name, second part is the field name, third (if any) is the unit
    # ignore third, build dict of dict of first part and second part
    def _split_component_field(key: str):
        component, field, *_ = key.split("__")
        return component, field

    split_values = [
        (*_split_component_field(key), value) for key, value in values.items()
    ]
    grouped_by_component = groupby(split_values, key=operator.itemgetter(0))
    combined_values = {
        component: non_fmu_simulation_inputs.get(component, {})
        | {
            field: Stamped(value=value, timestamp=timestamp)
            for _, field, value in field_values
        }
        for component, field_values in grouped_by_component
    }
    unused_non_fmu_simulation_inputs = {
        component_name: component
        for component_name, component in non_fmu_simulation_inputs.items()
        if component_name not in combined_values
    }
    with_extras = combined_values | unused_non_fmu_simulation_inputs

    return tuple([cls(**with_extras) for cls in clss])
