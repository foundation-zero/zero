"""Tests for what the contract states about the models' Python validators
(``thrs.spec.validators``): the recorded behaviour must predict what the
validators themselves do, so the bridge rejects - and snaps - exactly what the
API does."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Pump
from thrs.input_output.definitions.units import validate_ratio_within_precision
from thrs.spec.extension import EXTENSION_KEY, build_thrs_spec
from thrs.spec.validators import (
    CLAMP_KEY,
    FIELD_RULES_KEY,
    PYTHON_NAME_KEY,
    clamp_of,
    validation_error_url,
)


@pytest.fixture(scope="module")
def spec() -> dict[str, Any]:
    return build_thrs_spec()


def _walk(node: Any, key: str) -> list[Any]:
    if isinstance(node, dict):
        found = [node[key]] if key in node else []
        return found + [v for value in node.values() for v in _walk(value, key)]
    if isinstance(node, list):
        return [v for item in node for v in _walk(item, key)]
    return []


def _predicts(clamp: dict[str, Any], x: float) -> float | None:
    """What the recorded clamp says the validator does with ``x``: the
    (snapped) value, or None for a rejection."""
    if x < clamp.get("acceptBelow", -float("inf")) or x > clamp.get(
        "acceptAbove", float("inf")
    ):
        return None
    return min(max(x, clamp.get("minimum", x)), clamp.get("maximum", x))


def test_ratio_clamp_predicts_its_validator() -> None:
    clamp = clamp_of(validate_ratio_within_precision)
    assert (clamp["minimum"], clamp["maximum"]) == (0.0, 1.0)
    for x in (-1.0, -0.0002, -0.00005, 0.0, 0.3, 1.0, 1.00005, 1.0002, 5.0):
        try:
            actual: float | None = validate_ratio_within_precision(x)
        except ValueError as e:
            actual = None
            assert str(e) == clamp["error"].replace("{value}", str(x))
        assert _predicts(clamp, x) == actual, x


def test_every_clamp_in_the_spec_is_the_ratio_validator(spec) -> None:
    clamps = _walk(spec["components"], CLAMP_KEY)
    assert clamps, "no x-clamp recorded - is the Ratio after-validator still found?"
    assert all(c == clamp_of(validate_ratio_within_precision) for c in clamps)


def test_pump_dutypoint_rule_predicts_its_field_validator(spec) -> None:
    (rules,) = [
        s[FIELD_RULES_KEY]
        for s in spec["components"]["schemas"].values()
        if s.get("title") == "Pump" and FIELD_RULES_KEY in s
    ]
    (rule,) = rules
    assert rule["field"] == "Dutypoint" and rule["leaf"] == "Value"
    now = datetime.now(UTC)
    for x in (0.0, 0.05, 0.09999999999999999, 0.1, 0.5, 1.0):
        rejected = False
        try:
            Pump(
                dutypoint=Stamped(value=x, timestamp=now),
                on=Stamped(value=True, timestamp=now),
            )
        except ValidationError as e:
            rejected = any(err["loc"] == ("dutypoint",) for err in e.errors())
            assert rule["error"] in str(e)
        assert rejected == (x < rule["minimum"]), x


def test_every_model_property_names_its_python_field(spec) -> None:
    for name, schema in spec["components"]["schemas"].items():
        for key, prop in (schema.get("properties") or {}).items():
            assert PYTHON_NAME_KEY in prop, f"{name}.{key} has no {PYTHON_NAME_KEY}"


def test_validation_error_url_is_pydantics(spec) -> None:
    url = spec[EXTENSION_KEY]["validationErrorUrl"]
    assert url == validation_error_url()
    assert url.startswith("https://errors.pydantic.dev/") and url.endswith("/v/")
