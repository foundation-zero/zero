"""Describe the models' Python validators in the contract by probing them, not copying their code.

JSON Schema cannot express them, yet the bridge must reject exactly what the API rejects.
"""

from __future__ import annotations

import math
import operator
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ValidationError, create_model

from thrs.input_output.base import Stamped, ThrsValues

PYTHON_NAME_KEY = "x-python-name"
CLAMP_KEY = "x-clamp"
FIELD_RULES_KEY = "x-field-rules"

# Beyond this a probed interval is treated as unbounded.
_SEARCH_LIMIT = 1e300
_PROBE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


def validation_error_url() -> str:
    """The documentation link base pydantic appends each error type to."""

    class _Probe(BaseModel):
        value: int

    try:
        _Probe.model_validate({})
    except ValidationError as e:
        error = e.errors()[0]
        url = error.get("url")
        if url is None:
            raise RuntimeError("pydantic errors carry no documentation link") from e
        return url.removesuffix(error["type"])
    raise RuntimeError("pydantic accepted an empty model with a required field")


def _edge(
    accepts: Callable[[float], bool], start: float, direction: float
) -> float | None:
    """The last accepted float from ``start`` in ``direction``; None if unbounded."""
    step = 1.0
    good = start
    while True:
        candidate = start + direction * step
        if abs(candidate) > _SEARCH_LIMIT:
            return None
        if not accepts(candidate):
            bad = candidate
            break
        good = candidate
        step *= 2
    while True:
        middle = good + (bad - good) / 2
        if middle in (good, bad):
            return good
        if accepts(middle):
            good = middle
        else:
            bad = middle


def _message_template(
    render: Callable[[float], str],
    rejected: list[float],
    rendered: Callable[[float], str],
) -> str:
    """A ``{value}`` template of the rejection message, checked on every rejected value."""
    first = rejected[0]
    template = render(first).replace(rendered(first), "{value}")
    for value in rejected:
        if template.replace("{value}", rendered(value)) != render(value):
            raise RuntimeError(
                f"validator message {render(value)!r} is not a template on the value"
            )
    return template


def clamp_of(function: Callable[[float], float]) -> dict[str, Any]:
    """Describe a clamping number after-validator (``x-clamp``) by probing it."""

    def accepts(x: float) -> bool:
        try:
            function(x)
        except ValueError:
            return False
        return True

    if not accepts(0.0):
        raise RuntimeError(f"{function!r} rejects 0.0; cannot probe its interval")
    low, high = _edge(accepts, 0.0, -1.0), _edge(accepts, 0.0, 1.0)
    clamp: dict[str, Any] = {}
    rejected: list[float] = []
    if low is not None:
        clamp["minimum"] = function(low)
        clamp["acceptBelow"] = low
        rejected += [math.nextafter(low, -math.inf), low - 1.0]
    if high is not None:
        clamp["maximum"] = function(high)
        clamp["acceptAbove"] = high
        rejected += [math.nextafter(high, math.inf), high + 1.0]
    if not rejected:
        raise RuntimeError(f"{function!r} rejects nothing; not a clamp")

    def render(x: float) -> str:
        try:
            function(x)
        except ValueError as e:
            return str(e)
        raise RuntimeError(f"{function!r} accepted {x!r} it was probed to reject")

    clamp["error"] = _message_template(render, rejected, str)
    _check_clamp(function, clamp)
    return clamp


def _check_clamp(function: Callable[[float], float], clamp: dict[str, Any]) -> None:
    """Check in-range values pass unchanged and near-out-of-range values snap to the bound."""
    minimum, maximum = clamp.get("minimum"), clamp.get("maximum")
    lo = minimum if minimum is not None else -1e6
    hi = maximum if maximum is not None else 1e6
    for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = lo + (hi - lo) * fraction
        if function(x) != x:
            raise RuntimeError(f"{function!r} changes the in-range value {x!r}")
    for bound, edge in (
        (minimum, clamp.get("acceptBelow")),
        (maximum, clamp.get("acceptAbove")),
    ):
        if bound is not None and edge is not None and edge != bound:
            middle = bound + (edge - bound) / 2
            if function(middle) != bound or function(edge) != bound:
                raise RuntimeError(f"{function!r} does not snap to {bound!r}")


def is_pydantic_internal(function: Any) -> bool:
    """After-validators pydantic adds itself (``use_enum_values``)."""
    return isinstance(function, operator.attrgetter)


def field_rules_of(cls: type[BaseModel]) -> list[dict[str, Any]]:
    """Describe a model's stamped-number ``field_validator``s (``x-field-rules``)."""
    decorators = cls.__pydantic_decorators__.field_validators
    if not decorators:
        return []
    if not (isinstance(cls, type) and issubclass(cls, ThrsValues)):
        raise RuntimeError(
            f"field validators on {cls.__name__}: not a ThrsValues model"
        )
    base = _zero_instance(cls)
    rules: list[dict[str, Any]] = []
    for decorator in decorators.values():
        for name in decorator.info.fields:
            rule = _field_rule(cls, base, name)
            if rule is not None:
                rules.append(rule)
    return rules


def _zero_instance(cls: type[ThrsValues]) -> ThrsValues:
    """A valid instance of a component model, zeroed as by `ThrsValues.zero`."""
    holder = create_model("_ZeroHolder", component=(cls, ...), __base__=ThrsValues)
    return holder.zero().component  # type: ignore[attr-defined]


def _field_rule(
    cls: type[ThrsValues], base: ThrsValues, name: str
) -> dict[str, Any] | None:
    """The rule a field validator enforces, or None when it only transforms the value."""
    field = cls.model_fields[name]
    current = getattr(base, name)
    if not isinstance(current, Stamped) or not isinstance(current.value, float):
        raise RuntimeError(
            f"{cls.__name__}.{name}: only field validators on stamped numbers are supported"
        )

    def errors(x: float) -> list[Any]:
        values = {n: getattr(base, n) for n in cls.model_fields}
        values[name] = Stamped(value=x, timestamp=_PROBE_TIME)
        try:
            cls(**values)
        except ValidationError as e:
            return e.errors()
        return []

    def rule_rejects(x: float) -> bool:
        return any(e["loc"] == (name,) for e in errors(x))

    def leaf_accepts(x: float) -> bool:
        return not any(e["loc"][:1] == (name,) and len(e["loc"]) > 1 for e in errors(x))

    start = current.value
    if rule_rejects(start):
        raise RuntimeError(f"{cls.__name__}.{name}: the zero value is rejected")
    rule: dict[str, Any] = {"field": field.alias, "leaf": "Value"}
    rejected: list[float] = []
    for key, direction in (("minimum", -1.0), ("maximum", 1.0)):
        edge = _edge(
            lambda x: leaf_accepts(x) and not rule_rejects(x), start, direction
        )
        if edge is None:
            continue
        beyond = math.nextafter(edge, direction * math.inf)
        if leaf_accepts(beyond) and rule_rejects(beyond):
            rule[key] = edge
            rejected.append(beyond)
    if not rejected:
        return None

    def render(x: float) -> str:
        (error,) = [e for e in errors(x) if e["loc"] == (name,)]
        return str(error["ctx"]["error"])

    rule["error"] = _message_template(render, rejected, repr)
    (sample,) = [e for e in errors(rejected[0]) if e["loc"] == (name,)]
    stamped = sample["input"]
    rule["inputType"] = type(stamped).__name__
    rule["inputRepr"] = (
        repr(stamped)
        .replace(repr(stamped.timestamp), "{timestamp}")
        .replace(repr(stamped.value), "{value}", 1)
    )
    return rule
