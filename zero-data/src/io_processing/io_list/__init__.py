from dataclasses import dataclass
from typing import List


@dataclass
class IOValue:
    name: str
    data_type: str


@dataclass
class IOTopic:
    topic: str
    fields: List[IOValue]
