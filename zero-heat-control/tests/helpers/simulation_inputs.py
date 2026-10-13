from functools import partial
from typing import cast

import pytest
from pydantic import BaseModel

from thrs.input_output.base import ThrsValues
from thrs.input_output.fmu_mapping import included_in_fmu


def simulator_input_field_setters(cls: type[ThrsValues], ignore=None):
    if ignore is None:
        ignore = []
    for component_name, component in cls.model_fields.items():
        if component_name in ignore:
            continue
        for field_name, field in cast(
            BaseModel, component.annotation
        ).model_fields.items():
            if (component_name, field_name) in ignore:
                continue
            if included_in_fmu(field):

                def _setter(component_name, field_name, simulation_inputs, value):
                    component = getattr(simulation_inputs, component_name)
                    # We can't just update the value because we validate changes.
                    # BaseModel.model_copy skips validation
                    field = getattr(component, field_name)
                    new_field = field.model_copy(update={"value": value})
                    setattr(component, field_name, new_field)

                yield pytest.param(
                    partial(_setter, component_name, field_name),
                    id=f"{component_name}#{field_name}",
                )
