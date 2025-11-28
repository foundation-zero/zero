from datetime import datetime, timedelta
from functools import reduce
import operator
from typing import Any

from thrs.input_output.base import SimulationInputs, ThrsModel
from thrs.input_output.fmu_mapping import (
    build_outputs_from_fmu,
    extract_non_fmu_values,
)

from pydantic.fields import FieldInfo
from thrs.input_output.definitions.units import unit_for_annotation, unit_meta
from thrs.input_output.fmu_mapping import included_in_fmu
from thrs.simulation.fmu import Fmu


def flatten_model_values(model: ThrsModel, fmu_only: bool) -> dict[str, float]:
    def _values_for_component(component_name, component):
        def _name_for_field(field_name, field: FieldInfo):
            meta = unit_meta(unit_for_annotation(field.annotation))  # type: ignore
            if meta:
                return f"{component_name}__{field_name}__{meta.modelica_name}"
            else:
                return f"{component_name}__{field_name}"

        return {
            _name_for_field(field_name, field): getattr(component, field_name).value
            for field_name, field in {
                **type(component).model_fields,
                **type(component).model_computed_fields,
            }.items()
            if (included_in_fmu(field) if fmu_only else True)
        }

    vals = [
        _values_for_component(component_name, getattr(model, component_name))
        for component_name, component in {
            **type(model).model_fields,
            **type(model).model_computed_fields,
        }.items()
        if (included_in_fmu(component) if fmu_only else True)
    ]
    return reduce(operator.ior, vals, {})


class IoMapping[S: ThrsModel, C: ThrsModel, I: SimulationInputs, O: ThrsModel]:
    def __init__(
        self,
        fmu: Fmu,
        sensor_values_cls: type[S],
        simulation_outputs_cls: type[O],
    ):
        self._fmu = fmu
        self._sensor_values_cls = sensor_values_cls
        self._simulation_outputs_cls = simulation_outputs_cls

    def tick(
        self,
        control_values: C,
        simulation_inputs: I,
        time: datetime,
        tick_duration: timedelta,
    ) -> tuple[S, O, dict[str, Any]]:
        fmu_inputs = {
            **flatten_model_values(control_values, fmu_only=True),
            **flatten_model_values(simulation_inputs, fmu_only=True),
        }

        fmu_outputs = self._fmu.tick(
            fmu_inputs,
            tick_duration,
        )
        sensor_extra_values = extract_non_fmu_values(
            simulation_inputs, self._sensor_values_cls
        )

        sensor_values, simulation_outputs = build_outputs_from_fmu(
            (self._sensor_values_cls, self._simulation_outputs_cls),
            fmu_outputs,
            time + tick_duration,
            sensor_extra_values,
        )
        return (
            sensor_values,
            simulation_outputs,
            {**fmu_outputs, **fmu_inputs},
        )
