"""What every cross-API suite needs: talking GraphQL to the two services,
comparing what they answer, and seeding models with distinct values.

Timestamps compare as instants: the wire carries RFC 3339 and both APIs serve
it as a ``DateTime`` scalar, whose rendering (``Z`` or ``+00:00``) is not part
of the contract.
"""

from __future__ import annotations

import contextlib
import math
from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import ValidationError

from thrs.input_output.base import Stamped, ThrsValues

# Python and Rust format f64s differently - a 1-ULP display artifact, not a
# data difference.
FLOAT_REL_TOL = 1e-9


def post(
    url: str,
    query: str,
    variables: dict[str, Any] | None = None,
    *,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """POST a GraphQL document and return the response body (``data`` and/or
    ``errors``)."""
    response = httpx.post(
        url, json={"query": query, "variables": variables or {}}, timeout=timeout
    )
    response.raise_for_status()
    return response.json()


def query_data(url: str, query: str, variables: dict[str, Any] | None = None) -> Any:
    """POST a query that must succeed and return its ``data``."""
    body = post(url, query, variables)
    assert "errors" not in body, f"GraphQL errors from {url}: {body.get('errors')}"
    return body["data"]


def parse_ts(value: Any) -> datetime | None:
    """The instant an RFC 3339 string denotes, or None for anything else."""
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def recent(value: Any, window_s: float) -> bool:
    """Whether ``value`` is a timestamp within ``window_s`` of now."""
    instant = parse_ts(value)
    return (
        instant is not None
        and abs((datetime.now(UTC) - instant).total_seconds()) <= window_s
    )


def values_equal(a: Any, b: Any, *, ts_tol_s: float = 0.0) -> bool:
    """Deep parity compare. Floats agree within ``FLOAT_REL_TOL``; two
    timestamps agree when they denote the same instant, or instants within
    ``ts_tol_s`` seconds of each other (for fields the APIs stamp with their
    own ``now()``); everything else compares exactly."""
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(
            values_equal(a[k], b[k], ts_tol_s=ts_tol_s) for k in a
        )
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(
            values_equal(x, y, ts_tol_s=ts_tol_s) for x, y in zip(a, b, strict=True)
        )
    if _is_number(a) and _is_number(b):
        return math.isclose(float(a), float(b), rel_tol=FLOAT_REL_TOL, abs_tol=1e-12)
    ta, tb = parse_ts(a), parse_ts(b)
    if ta is not None and tb is not None:
        return abs((ta - tb).total_seconds()) <= ts_tol_s
    return a == b


def diff(
    a: Any,
    b: Any,
    path: str = "$",
    *,
    labels: tuple[str, str] = ("thrs-api", "mqtt-graphql"),
    ts_tol_s: float = 0.0,
    now_window_s: float | None = None,
    restamped: set[str] | None = None,
) -> list[str]:
    """Paths where two documents differ, for a readable assertion message.
    Values compare as in ``values_equal``; additionally, when ``now_window_s``
    is set, two timestamps both within that window of the wall clock count as
    equal (a field the APIs stamp at read time), and under ``restamped`` (a
    top-level key whose component the API restamped with its own ``now()``)
    a ``TimeStamp`` only has to be recent on both sides."""
    if isinstance(a, dict) and isinstance(b, dict):
        out: list[str] = []
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out.append(
                    f"{path}.{key}: only in {labels[0] if key in a else labels[1]}"
                )
                continue
            if (
                key == "TimeStamp"
                and restamped
                and any(
                    path == f"$.{r}" or path.startswith(f"$.{r}.") for r in restamped
                )
            ):
                if a[key] != b[key] and not (
                    recent(a[key], now_window_s or 0)
                    and recent(b[key], now_window_s or 0)
                ):
                    out.append(
                        f"{path}.{key}: not a recent timestamp ({a[key]!r} / {b[key]!r})"
                    )
                continue
            out += diff(
                a[key],
                b[key],
                f"{path}.{key}",
                labels=labels,
                ts_tol_s=ts_tol_s,
                now_window_s=now_window_s,
                restamped=restamped,
            )
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: list length {len(a)} != {len(b)}"]
        return [
            d
            for i, (x, y) in enumerate(zip(a, b, strict=True))
            for d in diff(
                x,
                y,
                f"{path}[{i}]",
                labels=labels,
                ts_tol_s=ts_tol_s,
                now_window_s=now_window_s,
                restamped=restamped,
            )
        ]
    if values_equal(a, b, ts_tol_s=ts_tol_s):
        return []
    if now_window_s is not None and recent(a, now_window_s) and recent(b, now_window_s):
        return []
    return [f"{path}: {labels[0]}={a!r} {labels[1]}={b!r}"]


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def graphql_literal(value: Any) -> str:
    """The GraphQL literal for a mutation argument: booleans, numbers, lists,
    and bare strings for enum member names."""
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(graphql_literal(v) for v in value) + "]"
    if isinstance(value, str):
        return value
    return repr(value)


def seed_distinct_values(model: ThrsValues) -> None:
    """Give every float leaf a distinct in-bounds value (bool/enum leaves and
    out-of-bounds units keep their zero() value), so parity is non-trivial."""
    counter = 0

    def visit(node: Any) -> None:
        nonlocal counter
        if isinstance(node, Stamped):
            counter += 1
            with contextlib.suppress(ValidationError, TypeError):
                node.value = 1.0 + counter * 0.01  # small, in-bounds for most units
            return
        if isinstance(node, ThrsValues):
            for attr in type(node).model_fields:
                visit(getattr(node, attr))

    visit(model)
