from typing import Any

from pydantic import BaseModel

from thrs.control.state import ControlModes, ControlState


class ModulePersistenceSnapshot(BaseModel):
    """Serialized control configuration snapshot of a single module."""

    parameters: dict[str, Any] | None = None
    control_mode: ControlModes = "manual"

    @classmethod
    def from_controller_state(cls, state: ControlState) -> ModulePersistenceSnapshot:
        return cls(
            parameters=state.parameters.model_dump(mode="json"),
            control_mode=state.automation_mode.mode,
        )
