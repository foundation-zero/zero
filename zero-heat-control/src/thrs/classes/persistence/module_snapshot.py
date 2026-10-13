from typing import Any

from pydantic import BaseModel

from thrs.control.switching import ControlModes


def _deep_diff(old: Any, new: Any, path: str) -> dict[str, tuple[Any, Any]]:
    """Recursively compare two (possibly nested dict) values, returning only the
    leaf values that differ, keyed by dotted path."""
    if isinstance(old, dict) and isinstance(new, dict):
        diffs: dict[str, tuple[Any, Any]] = {}
        for key in sorted(old.keys() | new.keys()):
            sub_path = f"{path}.{key}" if path else str(key)
            diffs.update(_deep_diff(old.get(key), new.get(key), sub_path))
        return diffs

    return {} if old == new else {path: (old, new)}


class ModulePersistenceSnapshot(BaseModel):
    """Serialized control configuration snapshot of a single module."""

    parameters: dict[str, Any] | None = None
    manual_control_values: dict[str, Any] | None = None
    control_mode: ControlModes = "manual"

    def _diff(self, other: "ModulePersistenceSnapshot") -> dict[str, tuple[Any, Any]]:
        """Return the leaf values that differ from another snapshot, as
        {dotted.path: (self_value, other_value)}. Nested dicts (e.g. per-actuator
        manual control values) are compared recursively so only the fields that
        actually changed show up, instead of the whole containing dict."""
        diffs: dict[str, tuple[Any, Any]] = {}
        for field in self.model_fields:
            diffs.update(_deep_diff(getattr(self, field), getattr(other, field), field))
        return diffs

    def value_diff(
        self, other: "ModulePersistenceSnapshot"
    ) -> dict[str, tuple[Any, Any]]:
        """Like diff(), but with Stamped `timestamp` leaves stripped out - only
        actual value changes remain."""
        return {
            path: change
            for path, change in self._diff(other).items()
            if path.rsplit(".", 1)[-1] != "timestamp"
        }

    def equals_ignoring_timestamps(self, other: "ModulePersistenceSnapshot") -> bool:
        """Whether this snapshot is equal to another once `timestamp` leaves
        (from Stamped values) are disregarded. Every Stamped value is re-stamped
        on every tick, so a plain `==`/diff() comparison never considers two
        snapshots equal even when no actual value changed."""
        return not self.value_diff(other)
