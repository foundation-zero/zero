from dataclasses import dataclass
from datetime import datetime
from pydantic import AliasGenerator, BaseModel, ConfigDict
from simulation.utils.string import hyphenize


class ThrsModel(BaseModel):
    """ThrsModel provides the conversion between the dashes in MQTT to Python underscores"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=hyphenize,
        )
    )


class Stamped[T](ThrsModel):
    value: T
    timestamp: datetime


@dataclass
class Meta:
    yard_tag: str
