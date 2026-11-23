from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel


class _TolerantStrEnum(StrEnum):
    """Maps values the AMCS adds later to ``UNKNOWN`` instead of failing a poll."""

    @classmethod
    def _missing_(cls, value: object) -> Self:
        return cls("Unknown")


class AlertPriority(_TolerantStrEnum):
    GEA = "GEA"
    EMERGENCY = "Emergency"
    ALARM = "Alarm"
    WARNING = "Warning"
    CAUTION = "Caution"
    EVENT = "Event"
    UNKNOWN = "Unknown"

    @property
    def rank(self) -> int:
        """Position in the AMCS hierarchy; severity is too coarse to filter on."""
        match self:
            case AlertPriority.GEA:
                return 5
            case AlertPriority.EMERGENCY:
                return 4
            case AlertPriority.ALARM:
                return 3
            case AlertPriority.WARNING | AlertPriority.UNKNOWN:
                return 2
            case AlertPriority.CAUTION:
                return 1
            case AlertPriority.EVENT:
                return 0

    @property
    def severity(self) -> int:
        """1 (least) to 5 (most severe); doubles as the ntfy priority."""
        match self:
            case AlertPriority.GEA | AlertPriority.EMERGENCY | AlertPriority.ALARM:
                return 5
            case AlertPriority.WARNING | AlertPriority.UNKNOWN:
                return 4
            case AlertPriority.CAUTION:
                return 3
            case AlertPriority.EVENT:
                return 1


class AlertUpdate(_TolerantStrEnum):
    ACTIVATED = "Activated"
    ACKNOWLEDGED = "Acknowledged"
    IDLE = "Idle"
    INHIBITED = "Inhibited"
    INVALID = "Invalid"
    UNBOUND = "Unbound"
    EVENT = "Event"
    UNKNOWN = "Unknown"


class Alert(BaseModel):
    id: int
    event_time: datetime
    priority: AlertPriority
    update: AlertUpdate
    system: str | None = None
    tag: str | None = None
    location: str | None = None
    description: str | None = None
