from abc import ABC, abstractmethod
from datetime import datetime
from functools import reduce
import operator
from typing import Any, cast

from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    ThrsValues,
    CombinedValues,
)
from thrs.input_output.fmu_mapping import (
    build_outputs_from_fmu,
    extract_non_fmu_values,
)

from pydantic.fields import FieldInfo
from thrs.input_output.definitions.units import unit_for_annotation, unit_meta
from thrs.input_output.fmu_mapping import included_in_fmu


def flatten_model_values(model: ThrsValues, fmu_only: bool) -> dict[str, float]:
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

    if isinstance(model, CombinedValues):
        vals = [
            flatten_model_values(values, fmu_only) for values in model.values.values()
        ]
        return reduce(operator.ior, vals, {})
    else:
        vals = [
            _values_for_component(component_name, getattr(model, component_name))
            for component_name, component in {
                **type(model).model_fields,
                **type(model).model_computed_fields,
            }.items()
            if (included_in_fmu(component) if fmu_only else True)
        ]
        return reduce(operator.ior, vals, {})


class IoMapping[S, C, I, O](ABC):
    @abstractmethod
    def generate_inputs(
        self, control_values: C, simulation_inputs: I
    ) -> dict[str, Any]: ...

    @abstractmethod
    def construct_outputs(
        self,
        fmu_inputs: dict[str, Any],
        fmu_outputs: dict[str, Any],
        simulation_inputs: I,
        time: datetime,
    ) -> tuple[S, O, dict[str, Any]]: ...


class CombinedIoMapping[I: SimulationInputs, O: SimulationValues](
    IoMapping[CombinedValues, CombinedValues, I, O]
):
    def __init__(
        self,
        sensor_values_clss: dict[str, type[ThrsValues]],
        simulation_outputs_cls: type[O],
    ):
        self._sensor_values_clss = sensor_values_clss
        self._simulation_outputs_cls = simulation_outputs_cls

    def generate_inputs(
        self,
        control_values: CombinedValues,
        simulation_inputs: I,
    ) -> dict[str, Any]:
        return {
            **{
                key: value
                for model in control_values.values.values()
                for key, value in flatten_model_values(model, fmu_only=True).items()
            },
            **flatten_model_values(simulation_inputs, fmu_only=True),
        }

    def construct_outputs(
        self,
        fmu_inputs: dict[str, Any],
        fmu_outputs: dict[str, Any],
        simulation_inputs: I,
        time: datetime,
    ) -> tuple[CombinedValues, O, dict[str, Any]]:
        # build simulation outputs from FMU outputs alone
        (simulation_outputs,) = build_outputs_from_fmu(
            (self._simulation_outputs_cls,),
            fmu_outputs,
            time,
        )

        # extract non-FMU values from both simulation inputs and outputs
        non_fmu_values = {
            key: value
            for sensor_values_cls in self._sensor_values_clss.values()
            for source in (simulation_inputs, simulation_outputs)
            for key, value in extract_non_fmu_values(source, sensor_values_cls).items()
        }

        # build sensor values with the combined non-FMU values
        sensor_values = build_outputs_from_fmu(
            tuple(self._sensor_values_clss.values()),
            fmu_outputs,
            time,
            non_fmu_values,
        )
        return (
            CombinedValues(dict(zip(self._sensor_values_clss.keys(), sensor_values))),
            simulation_outputs,
            {**fmu_outputs, **fmu_inputs},
        )


class ThrsModelIoMapping[
    S: ThrsValues,
    C: ThrsValues,
    I: SimulationInputs,
    O: SimulationValues,
](IoMapping[S, C, I, O]):
    def __init__(
        self,
        sensor_values_cls: type[S],
        simulation_outputs_cls: type[O],
    ):
        self._sub = CombinedIoMapping({"": sensor_values_cls}, simulation_outputs_cls)

    def generate_inputs(
        self, control_values: C, simulation_inputs: I
    ) -> dict[str, Any]:
        return self._sub.generate_inputs(
            CombinedValues({"": control_values}), simulation_inputs
        )

    def construct_outputs(
        self,
        fmu_inputs: dict[str, Any],
        fmu_outputs: dict[str, Any],
        simulation_inputs: I,
        time: datetime,
    ) -> tuple[S, O, dict[str, Any]]:
        sensor_values, outputs, raw = self._sub.construct_outputs(
            fmu_inputs, fmu_outputs, simulation_inputs, time
        )
        return cast(S, sensor_values.values[""]), outputs, raw
