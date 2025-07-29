from dataclasses import dataclass
from typing import List, Literal
from polars import DataFrame

type Source = Literal["marpower", "vitters"]


@dataclass
class IOValue:
    name: str
    data_type: str


@dataclass
class IOTopic:
    topic: str
    fields: List[IOValue]


@dataclass
class IOResult:
    io_list: DataFrame
    topics: List[IOTopic]
