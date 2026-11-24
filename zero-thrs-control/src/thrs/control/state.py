from datetime import UTC, datetime
from typing import Literal, Self, cast

from thrs.input_output.base import ThrsValues, zero_component

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

    @classmethod
    def zero(cls, timestamp: datetime | None = None) -> Self:
        """The module's controllers at their zero values, stamped at `timestamp` or
        now, with the default parameters and the defaults above."""
        stamped_at = timestamp or datetime.now(UTC)
        parameters_cls = cast(
            type[ThrsValues], cls.model_fields["parameters"].annotation
        )
        return cls(
            **{
                name: zero_component(field.annotation, stamped_at)
                for name, field in cls.model_fields.items()
                if name not in ControlState.model_fields
            },
            parameters=parameters_cls(),
        )
