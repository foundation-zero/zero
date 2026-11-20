from typing import Any

from pydantic import BaseModel

from thrs.control.state import ControlModes


class ModulePersistenceSnapshot(BaseModel):
    """Serialized control configuration snapshot of a single module."""

    parameters: dict[str, Any] | None = None
    control_mode: ControlModes = "manual"
