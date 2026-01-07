import json
from dataclasses import dataclass
from typing import Protocol, TypeVar

T = TypeVar("T")


class Generator[T](Protocol):
    def gen(self) -> T: ...


@dataclass
class JSONGenerator(Generator):
    """
    Wrapper around other Generator instances that expose Generator interface itself.
    Produces JSON values
    """

    values: dict[str, Generator]

    def gen(self):
        return json.dumps(
            {field: generator.gen() for field, generator in self.values.items()}
        )


@dataclass
class GeneratorConfig:
    topic: str
    interval: int
    generator: Generator

    def determine_values(self):
        return str(self.generator.gen())
