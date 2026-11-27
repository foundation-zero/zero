from datetime import UTC, datetime
from enum import Enum

from pydantic import Field

from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.units import Seconds


class AmcsMode(Enum):
    LOCAL = 0
    MANUAL = 1
    AUTO = 2
    EXTERNAL = 3


class AmcsModeStatus(ThrsValues):
    mode: Stamped[AmcsMode]

    @classmethod
    def create_advisory(cls) -> AmcsModeStatus:
        return cls(mode=Stamped.stamp(value=AmcsMode.EXTERNAL))

    @property
    def is_advisory(self) -> bool:
        return self.mode.value == AmcsMode.EXTERNAL.value


class AmcsExternalAvailable(ThrsValues):
    since: Stamped[Seconds] = Field(
        default_factory=lambda: Stamped.stamp(datetime.now(UTC).timestamp())
    )


__all__ = [
    "AmcsExternalAvailable",
    "AmcsModeStatus",
]
