from dataclasses import dataclass
from typing import Literal

from polars import DataFrame

type Source = Literal["marpower", "sail_system"]


@dataclass(frozen=True, eq=True)
class IOValue:
    name: str
    data_type: str

    @staticmethod
    def from_json_path(json_path: str, data_type: str) -> "IOValue":
        return IOValue(
            name=json_path[2:],
            data_type=data_type,
        )


@dataclass(frozen=True, eq=True)
class IOTopic:
    topic: str
    fields: list[IOValue]
    group: str | None = None


@dataclass(frozen=True, eq=True)
class IOResult:
    io_list: DataFrame
    topics: list[IOTopic]
