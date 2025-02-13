from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel
from simulation.utils.string import hyphenize


class ThrsModel(BaseModel):
    """ThrsModel provides the conversion between the dashes in MQTT to Python underscores"""

    class Config:
        alias_generator = hyphenize


class Stamped[T](ThrsModel):
    value: T
    timestamp: datetime


@dataclass
class Meta:
    yard_tag: str
