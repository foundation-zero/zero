from dataclasses import dataclass
from typing import Protocol, TypeVar

T = TypeVar("T")


class Generator[T](Protocol):
    def gen(self) -> T: ...


@dataclass
class GeneratorConfig:
    topic: str
    interval: int
    values: dict[str, Generator]
