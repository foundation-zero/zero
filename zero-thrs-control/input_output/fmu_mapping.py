import operator
from datetime import datetime
from functools import reduce

from pydantic.fields import FieldInfo

from input_output.base import Stamped, ThrsModel
from input_output.units import unit_meta


def groupby(iterable, key):
    from itertools import groupby as _groupby

    data = sorted(iterable, key=key)
    return _groupby(data, key)


def build_inputs_for_fmu(
    model: ThrsModel,
) -> dict[str, float]:
    def _values_for_component(component_name, component):
        def _name_for_field(field_name, field: FieldInfo):
            meta = unit_meta(field.annotation.unit())  # type: ignore
            if meta:
                return f"{component_name}__{field_name}__{meta.modelica_name}"
            else:
                return f"{component_name}__{field_name}"

        return {
            _name_for_field(field_name, field): getattr(component, field_name).value
            for field_name, field in component.model_fields.items()
        }

    vals = [
        _values_for_component(component_name, getattr(model, component_name))
        for component_name in model.model_fields.keys()
    ]
    return reduce(operator.ior, vals, {})


def build_outputs_from_fmu(
    clss: list[type[ThrsModel]],
    values: dict[str, float],
    timestamp: datetime,
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
        component: {
            field: Stamped(value=value, timestamp=timestamp)
            for _, field, value in field_values
        }
        for component, field_values in grouped_by_component
    }

    return [cls(**nested_values) for cls in clss]
