from datetime import UTC, datetime
from enum import Enum

from pydantic import Field

from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.units import Seconds


class ControlMode(Enum):
    LOCAL = 0
    MANUAL = 1
    AUTO = 2
    EXTERNAL = 3


class AmcsControlMode(ThrsValues):
    mode: Stamped[ControlMode]

    @classmethod
    def create_advisory(cls) -> "AmcsControlMode":
        return cls(mode=Stamped.stamp(value=ControlMode.EXTERNAL))

    @property
    def is_advisory(self) -> bool:
        return self.mode.value == ControlMode.EXTERNAL.value


class AmcsExternalAvailable(ThrsValues):
    since: Stamped[Seconds] = Field(
        default_factory=lambda: Stamped.stamp(datetime.now(UTC).timestamp())
    )


__all__ = [
    "AmcsControlMode",
    "AmcsExternalAvailable",
]
