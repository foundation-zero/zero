from dataclasses import dataclass
from typing import Literal

from polars import DataFrame

type Source = Literal["marpower", "sail_system", "atpx"]


@dataclass(frozen=True, eq=True)
class IOValue:
    name: str
    data_type: str
    yard_tag: str | None = None

    @staticmethod
    def from_json_path(
        json_path: str, data_type: str, yard_tag: str | None
    ) -> "IOValue":
        return IOValue(
            name=json_path[2:],
            data_type=data_type,
            yard_tag=yard_tag,
        )


@dataclass(frozen=True, eq=True)
class IOTopic:
    topic: str
    fields: list[IOValue]
    group: str | None = None

    @property
    def yard_tag(self) -> str | None:
        return next(
            (field.yard_tag for field in self.fields if field.yard_tag),
            None,
        )


@dataclass(frozen=True, eq=True)
class IOResult:
    io_list: DataFrame
    topics: list[IOTopic]
