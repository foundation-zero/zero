from collections import Counter
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from inspect import getmembers
from typing import Callable


class Severity(Enum):
    WARNING = "warning"
    ALARM = "alarm"


@dataclass
class Alarm:
    code: str
    severity: Severity


class BaseAlarms[Sensors, ControlValues, Control]:
    def __init__(self) -> None:
        self._checks = getmembers(
            self, lambda f: hasattr(f, "__alarm_code__") and f.__alarm_code__
        )
        codes = [f.__alarm_code__ for _, f in self._checks]
        duplicates = [item for item, count in Counter(codes).items() if count > 1]
        if duplicates:
            raise ValueError(
                f"Duplicate alarm codes found: {duplicates}. Each alarm code must be unique."
            )

    def check(
        self, sensor_values: Sensors, control_values: ControlValues, control: Control
    ) -> list[Alarm]:
        def _check():
            for _, f in self._checks:
                alarm = f(sensor_values, control_values, control)
                if alarm is not None:
                    yield alarm

        return list(_check())


def alarm[**P](
    code: str, severity: Severity
) -> Callable[[Callable[P, bool]], Callable[P, Alarm | None]]:
    def _check(f: Callable[P, bool]):
        @wraps(f)
        def _do(*args: P.args, **kwargs: P.kwargs) -> Alarm | None:
            if f(*args, **kwargs):
                return Alarm(code, severity)
            else:
                return None

        _do.__alarm_code__ = code  # type: ignore
        return _do

    return _check
