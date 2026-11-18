import math
from typing import Any

from thrs.input_output.base import Stamped, ThrsValues

FLOAT32_RELATIVE_TOLERANCE = 2**-23
"""Floats that differ less than one float32 step, relatively, are the same value:
the AMCS reports floats rounded to float32."""


def actuated_as_commanded[V: ThrsValues](actuated: V, commanded: V) -> V:
    """A copy of the actuated values in which each leaf that matches its command is the command.

    The AMCS restamps actuated values with its own clock and rounds floats to
    float32, so without this a client never sees exactly what it set.
    """
    published = actuated.model_copy(deep=True)
    _take_matching_commands(published, commanded)
    return published


def _take_matching_commands(actuated: ThrsValues, commanded: ThrsValues) -> None:
    for name in type(actuated).model_fields:
        actuated_field = getattr(actuated, name)
        matched = _matched(actuated_field, getattr(commanded, name))
        if matched is not actuated_field:
            setattr(actuated, name, matched)


def _matched(actuated: Any, commanded: Any) -> Any:
    """The command when this leaf matches it, else the actuated value, updated in place."""
    if isinstance(actuated, Stamped):
        if _same_value(actuated.value, commanded.value):
            return commanded.model_copy()
    elif isinstance(actuated, ThrsValues):
        _take_matching_commands(actuated, commanded)
    elif isinstance(actuated, list):
        actuated[:] = [
            _matched(actuated_item, commanded_item)
            for actuated_item, commanded_item in zip(actuated, commanded, strict=True)
        ]
    return actuated


def _same_value(actuated: Any, commanded: Any) -> bool:
    if isinstance(actuated, float) and isinstance(commanded, float):
        return math.isclose(actuated, commanded, rel_tol=FLOAT32_RELATIVE_TOLERANCE)
    return actuated is not None and actuated == commanded
