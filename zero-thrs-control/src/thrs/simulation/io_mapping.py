import operator
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from functools import reduce
from typing import Any, cast

from thrs.input_output.base import CombinedValues, ThrsValues
from thrs.input_output.fmu_mapping import (
    build_fmu_key_mapping,
    build_outputs_from_fmu,
    extract_non_fmu_values,
)
from thrs.orchestration.module import ModuleClassMap


def get_value(model, component: str, field: str) -> Any:
    val = getattr(getattr(model, component), field).value
    if isinstance(val, Enum):
        return val.value
    return val


type KeyMapping = Callable[[type[ThrsValues]], dict[tuple[str, str], str]]


def flatten_model_values(
    model: ThrsValues | CombinedValues, key_mapping: KeyMapping
) -> dict[str, float]:
    """The model's values by key, the keys and what they hold coming from `key_mapping`.

    It maps a model's class to `{(component, field): key}`, so each model of combined
    values is flattened with keys of its own.
    """
    if isinstance(model, CombinedValues):
        return reduce(
            operator.ior,
            [flatten_model_values(v, key_mapping) for v in model.values.values()],
            {},
        )
    return {
        key: get_value(model, component, field)
        for (component, field), key in key_mapping(type(model)).items()
    }


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
        control_values: C,
        simulation_inputs: I,
        time: datetime,
    ) -> tuple[S, O, dict[str, Any]]: ...


class CombinedIoMapping[I: ThrsValues, O: ThrsValues](
    IoMapping[CombinedValues, CombinedValues, I, O]
):
    def __init__(
        self,
        sensor_values_clss: ModuleClassMap,
        simulation_outputs_cls: type[O],
    ):
        self._sensor_values_clss = sensor_values_clss
        self._simulation_outputs_cls = simulation_outputs_cls

        self._fmu_key_mapping_cache: dict[
            type[ThrsValues], dict[tuple[str, str], str]
        ] = {}

    def _fmu_key_mapping(
        self, model_cls: type[ThrsValues]
    ) -> dict[tuple[str, str], str]:
        if model_cls not in self._fmu_key_mapping_cache:
            self._fmu_key_mapping_cache[model_cls] = build_fmu_key_mapping(model_cls)
        return self._fmu_key_mapping_cache[model_cls]

    def generate_inputs(
        self,
        control_values: CombinedValues,
        simulation_inputs: I,
    ) -> dict[str, Any]:
        return {
            **flatten_model_values(control_values, self._fmu_key_mapping),
            **flatten_model_values(simulation_inputs, self._fmu_key_mapping),
        }

    def construct_outputs(
        self,
        fmu_inputs: dict[str, Any],
        fmu_outputs: dict[str, Any],
        control_values: CombinedValues,
        simulation_inputs: I,
        time: datetime,
    ) -> tuple[CombinedValues, O, dict[str, Any]]:
        (simulation_outputs,) = build_outputs_from_fmu(
            (self._simulation_outputs_cls,),
            fmu_outputs,
            time,
        )

        non_fmu_values = {
            key: value
            for module_name, sensor_values_cls in self._sensor_values_clss.items()
            for source in (
                simulation_inputs,
                simulation_outputs,
                control_values.values[module_name],
            )
            for key, value in extract_non_fmu_values(source, sensor_values_cls).items()
        }

        sensor_values = build_outputs_from_fmu(
            tuple(self._sensor_values_clss.values()),
            fmu_outputs,
            time,
            non_fmu_values,
        )
        return (
            CombinedValues(
                dict(zip(self._sensor_values_clss.keys(), sensor_values, strict=False))
            ),
            simulation_outputs,
            {**fmu_outputs, **fmu_inputs},
        )


class ThrsModelIoMapping[
    S: ThrsValues,
    C: ThrsValues,
    I: ThrsValues,
    O: ThrsValues,
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
        control_values: C,
        simulation_inputs: I,
        time: datetime,
    ) -> tuple[S, O, dict[str, Any]]:
        sensor_values, outputs, raw = self._sub.construct_outputs(
            fmu_inputs,
            fmu_outputs,
            CombinedValues({"": control_values}),
            simulation_inputs,
            time,
        )
        return cast(S, sensor_values.values[""]), outputs, raw
