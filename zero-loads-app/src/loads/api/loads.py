from typing import Any, Callable, Protocol

import loads.sensors.sensors as sensors
from loads.sensors import LoadsModel


class LoadsField[T: LoadsModel](Protocol):
    model: type[T]

    def give(self, data: T) -> Any: ...


class LoadField[T: LoadsModel]:
    def __init__(self, model: type[T], field: str) -> None:
        self.model = model
        self._field = field

    def give(self, data: T | None) -> float | None:
        if data:
            return getattr(data, self._field)
        else:
            return None


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
    "main-sheet-load": LoadField(sensors.MainSheetCaptiveWinch, "torque"),
    "main-vang-load": LoadField(sensors.MainVang, "load"),
    "main-vang-load-fn": FnField(sensors.MainVang, lambda x: x.load + x.load_2),
}
