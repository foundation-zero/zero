from typing import Literal

from thrs.input_output.base import ThrsValues

type ControlModes = Literal["manual", "automatic"]


class AutomationMode(ThrsValues):
    mode: ControlModes


class ControlMode(ThrsValues):
    def __str__(self):
        values = [
            getattr(self, field_name)
            if isinstance(getattr(self, field_name), str)
            else f"{field_name}: {getattr(self, field_name)!s}"
            for field_name, field_info in type(self).model_fields.items()
        ]

        return ", ".join(values)


class ControlState[C: ThrsValues, P: ThrsValues, M: ThrsValues](ThrsValues):
    """What a module's controller publishes about itself, besides its own controllers.

    A module's controller state subclasses this and adds its controllers as components.
    """

    automation_mode: AutomationMode = AutomationMode(mode="manual")
    # The manual controls, which Switching fills; `None` only without it.
    manual_values: C | None = None
    # The automatic control's mode, `None` while manual.
    control_mode: M | None = None
    parameters: P
