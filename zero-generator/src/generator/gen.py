import random
from datetime import UTC, datetime
from functools import partial
from typing import Callable, Literal, TypeVar, assert_never, cast

from .base import Generator

T = TypeVar("T")

type GeneratorType = Literal["bool", "int", "float", "str", "timestamp", "choice"]


def validate_type(type: str) -> GeneratorType:
    try:
        type = cast(GeneratorType, type)
        return type
    except Exception:
        raise ValueError(f"Invalid generator type: {type}")


class FnGenerator[T](Generator[T]):
    def __init__(self, fn: Callable[[], T]):
        self._fn = fn

    def gen(self, *args, **kwargs) -> T:
        return self._fn(*args, **kwargs)


def ensure_bounds(lt: int | float, gt: int | float):
    if lt >= gt:
        raise ValueError(f"Lower bound must be less than upper bound: {lt} >= {gt}")


def int_(lt=0, gt=100) -> Generator[int]:
    ensure_bounds(lt, gt)
    return FnGenerator(partial(random.randint, lt, gt))


def float_(lt=0.0, gt=100.0) -> Generator[float]:
    ensure_bounds(lt, gt)
    return FnGenerator(partial(random.uniform, lt, gt))


def str_(length=10) -> Generator[str]:
    return FnGenerator(lambda: "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length)))


def bool_() -> Generator:
    return FnGenerator(partial(random.choice, [True, False]))


def choice[T](options: list[T]) -> Generator[T]:
    return FnGenerator(partial(random.choice, options))


def timestamp() -> Generator[datetime]:
    return FnGenerator(lambda: datetime.now(tz=UTC))


def _lookup(type: GeneratorType) -> Callable[..., Generator]:
    match type:
        case "bool":
            return bool_
        case "int":
            return int_
        case "float":
            return float_
        case "str":
            return str_
        case "timestamp":
            return timestamp
        case "choice":
            return choice
        case _:
            assert_never(type)


def create_generator(type: GeneratorType, *args, **kwargs) -> Generator:
    return _lookup(type)(*args, **kwargs)
