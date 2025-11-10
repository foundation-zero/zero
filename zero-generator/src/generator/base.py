import random
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any


class Generator(ABC):
    @abstractmethod
    def gen(self) -> Any: ...


class RandomNumberGenerator(Generator):
    def __init__(self, type: str, lt: float | None = None, gt: float | None = None):
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


class RandomGenerator(Generator):
    def __init__(self, type: str):
        self._type: str = type

    def gen(self):
        match self._type:
            case "boolean":
                return random.choice([True, False])
            case "string":
                return "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))
            case "timestamp":
                return datetime.now(tz=UTC)
            case _:
                raise ValueError(f"Unsupported data type: {self._type}")


class RandomChoiceGenerator(Generator):
    def __init__(self, type: str, options: list):
        self._type: str = type
        self._options: list = options

        if not options:
            raise ValueError("Options list cannot be empty.")

    def gen(self):
        return random.choice(self._options)


class GeneratorFactory:
    @staticmethod
    def create(type: str, *args, **kwargs) -> Generator:
        match type:
            case "int" | "float":
                return RandomNumberGenerator(type, *args, **kwargs)
            case "boolean" | "string" | "timestamp":
                return RandomGenerator(type, *args, **kwargs)
            case "enum":
                return RandomChoiceGenerator(type, *args, **kwargs)
            case _:
                raise ValueError(f"Unknown generator type: {type}")
