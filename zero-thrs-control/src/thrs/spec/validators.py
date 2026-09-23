"""What the models' Python validators do, stated in the contract.

A JSON Schema says a number's bounds and a tuple's length, but not what a
Python validator does. The bridge must reject (and word the rejection of)
exactly what the API rejects, so the validators the mutable models carry are
described here - not by copying their code, but by *asking* them: each one is
run against probe values and its behaviour recorded, then that record is
checked against the validator again.

* ``x-python-name`` (every model property): the Python field name, which
  pydantic's error locations and model reprs use.
* ``x-clamp`` (a number wrapped by an after-validator such as ``Ratio``'s):
  the accepted interval, the bounds out-of-range-but-close values snap to,
  and the rejection message as a ``{value}`` template.
* ``x-field-rules`` (a model with ``field_validator``s such as ``Pump``'s):
  per validated stamped field, the interval its leaf must stay in and the
  rejection message.
* ``validationErrorUrl`` (the extension root): the documentation link base
  pydantic appends each error type to.
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

# How far the probes search for an interval's edge: beyond this a number is
# treated as unbounded.
_SEARCH_LIMIT = 1e300
# A known timestamp for probe values (a validator may only look at the value).
_PROBE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


def validation_error_url() -> str:
    """The base of the documentation link pydantic appends to every error,
    read off an error pydantic raises."""

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
    """The last accepted float going from the accepted ``start`` in
    ``direction``, exact to the float; None when nothing within the search
    limit is rejected."""
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
    """A ``{value}`` template for the message ``render`` gives each rejected
    value, checked on every one of them."""
    first = rejected[0]
    template = render(first).replace(rendered(first), "{value}")
    for value in rejected:
        if template.replace("{value}", rendered(value)) != render(value):
            raise RuntimeError(
                f"validator message {render(value)!r} is not a template on the value"
            )
    return template


def clamp_of(function: Callable[[float], float]) -> dict[str, Any]:
    """Describe a number after-validator by running it: the interval it
    accepts (``acceptBelow`` .. ``acceptAbove``), the bounds values beyond
    ``minimum``/``maximum`` snap to, and its rejection message."""

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
    """The recorded behaviour, checked: values inside the bounds pass through
    unchanged, values between a bound and its accept edge snap to the bound."""
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
    """Describe a model's ``field_validator``s on stamped numeric fields by
    running them: the interval the leaf value must stay in (within the range
    the leaf type itself accepts) and the rejection message."""
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
    """A valid instance of a component model, zeroed the way `ThrsValues.zero`
    zeroes a model's components (honouring each field's `zero_value`)."""
    holder = create_model("_ZeroHolder", component=(cls, ...), __base__=ThrsValues)
    return holder.zero().component  # type: ignore[attr-defined]


def _field_rule(
    cls: type[ThrsValues], base: ThrsValues, name: str
) -> dict[str, Any] | None:
    """The rule a field validator enforces on a stamped number, or None when
    it rejects nothing (it only transforms the value)."""
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
