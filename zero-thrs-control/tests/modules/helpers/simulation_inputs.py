from functools import partial
from typing import cast
from pydantic import BaseModel
import pytest
from input_output.base import SimulationInputs
from input_output.fmu_mapping import included_in_fmu


def simulator_input_field_setters(cls: type[SimulationInputs], ignore=None):
    if ignore is None:
        ignore = []
    for component_name, component in cls.model_fields.items():
        if component_name in ignore:
            continue
        for field_name, field in cast(
            BaseModel, component.annotation
        ).model_fields.items():
            if included_in_fmu(field):

                def _setter(component_name, field_name, simulation_inputs, value):
                    getattr(
                        getattr(simulation_inputs, component_name), field_name
                    ).value = value

                yield pytest.param(
                    partial(_setter, component_name, field_name),
                    id=f"{component_name}#{field_name}",
                )
