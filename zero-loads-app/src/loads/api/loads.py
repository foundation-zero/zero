from typing import Any, Callable, Literal, Protocol

import loads.sensors.sensors as sensors
from loads.sensors import LoadsModel

Fields = Literal[
    "torque",
    "load",
    "load_2",
    "position",
    "position_2",
    "relative_position",
    "relative_position_2",
    "rotational_speed",
]


class LoadsField[T: LoadsModel](Protocol):
    model: type[T]

    def give(self, data: T) -> Any: ...


class LoadField[T: LoadsModel]:
    def __init__(self, model: type[T], field: Fields) -> None:
        self.model = model
        self._field = field

    def give(self, data: T | None) -> float | None:
        return getattr(data, self._field) if data else None


class FnField[T: LoadsModel]:
    def __init__(self, model: type[T], fn: Callable[[T], float]) -> None:
        self.model = model
        self._fn = fn

    def give(self, data: T | None) -> float | None:
        if data:
            return self._fn(data)
        else:
            return None


loads_variables: dict[str, LoadsField] = {
    "main-sheet-load": LoadField(sensors.BladeCunningham, "load"),
    "main-vang-load": LoadField(sensors.MainVang, "load"),
    "main-sheet-position": LoadField(sensors.BladeCunningham, "relative_position"),
}
