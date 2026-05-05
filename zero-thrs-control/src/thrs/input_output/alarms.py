from collections import Counter
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from inspect import getmembers
from typing import Callable

from thrs.input_output.base import ThrsValues


class Severity(Enum):
    WARNING = "warning"
    ALARM = "alarm"


@dataclass
class Alarm:
    code: str
    message: str
    severity: Severity


class BaseAlarms[SensorValues, ControlValues]:
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
        self,
        sensor_values: SensorValues,
        control_values: ControlValues,
        parameters: ThrsValues,
    ) -> list[Alarm]:
        def _check():
            for _, f in self._checks:
                alarm = f(sensor_values, control_values, parameters)
                if alarm is not None:
                    yield alarm

        return list(_check())


def alarm[**P](
    code: str, severity: Severity
) -> Callable[[Callable[P, str | None]], Callable[P, Alarm | None]]:
    def _check(f: Callable[P, str | None]):
        @wraps(f)
        def _do(*args: P.args, **kwargs: P.kwargs) -> Alarm | None:
            message = f(*args, **kwargs)
            return Alarm(code, message, severity) if message is not None else None

        _do.__alarm_code__ = code  # type: ignore
        return _do

    return _check
