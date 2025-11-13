import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal, TypeVar

T = TypeVar("T")


class Generator(ABC):
    @abstractmethod
    def gen(self) -> Any: ...


@dataclass
class GeneratorConfig:
    topic: str
    interval: int
    values: dict[str, Generator]


class RandomNumberGenerator(Generator):
    def __init__(self, type: Literal["int", "float"], lt: float | None = None, gt: float | None = None):
        self._type: str = type

        self._lt = lt if lt is not None else 0
        self._gt = gt if gt is not None else 100

        if self._lt >= self._gt:
            raise ValueError(f"Lower bound must be less than upper bound: {self._lt} >= {self._gt}")

    def gen(self):
        match self._type:
            case "int":
                return random.randint(int(self._lt), int(self._gt))
            case "float":
                return round(random.uniform(self._lt, self._gt), 2)
            case _:
                raise ValueError(f"Unsupported data type: {self._type}")


class RandomBoolGenerator(Generator):
    def __init__(self, type: Literal["bool"]):
        self._type: str = type

    def gen(self):
        return random.choice([True, False])


class RandomStringGenerator(Generator):
    def __init__(self, type: Literal["str"]):
        self._type: str = type

    def gen(self):
        return "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))


class DateGenerator(Generator):
    def __init__(self, type: Literal["timestamp"]):
        self._type: str = type

    def gen(self) -> datetime:
        return datetime.now(tz=UTC)


class RandomChoiceGenerator[T](Generator):
    def __init__(self, type: Literal["enum"], options: list[T]):
        self._type: str = type
        if not options:
            raise ValueError("Options list cannot be empty.")
        self._options: list[T] = options

    def gen(self) -> T:
        return random.choice(self._options)


def create_generator(type: str, *args, **kwargs) -> Generator:
    match type:
        case "int" | "float":
            return RandomNumberGenerator(type, *args, **kwargs)
        case "str":
            return RandomStringGenerator(type, *args, **kwargs)
        case "bool":
            return RandomBoolGenerator(type, *args, **kwargs)
        case "timestamp":
            return DateGenerator(type)
        case "enum":
            return RandomChoiceGenerator(type, *args, **kwargs)
        case _:
            raise ValueError(f"Unknown generator type: {type}")
