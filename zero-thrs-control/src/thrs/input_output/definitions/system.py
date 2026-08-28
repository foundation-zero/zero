from enum import Enum

from thrs.input_output.base import Stamped, ThrsValues


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


__all__ = [
    "AmcsControlMode",
]
