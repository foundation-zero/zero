from dataclasses import dataclass
from typing import List, Literal
from polars import DataFrame

type Source = Literal["marpower", "vitters"]


@dataclass
class IOValue:
    name: str
    data_type: str
    
    @staticmethod
    def from_json_path(json_path: str, data_type: str) -> "IOValue":
        return IOValue(
            name=json_path[2:],
            data_type=data_type,
        )


@dataclass
class IOTopic:
    topic: str
    fields: List[IOValue]


@dataclass
class IOResult:
    io_list: DataFrame
    topics: List[IOTopic]
