from datetime import datetime
from typing import Protocol
import polars as pl


class Collector(Protocol):
    def collect(self, values: dict[str, float], time: datetime): ...


class NullCollector(Collector):
    def collect(self, values: dict[str, float], time: datetime):
        pass


class PolarsCollector(Collector):
    def __init__(self):
        self._data = None
        self._times = pl.Series("time", dtype=pl.Datetime)

    def collect(self, values: dict[str, float], time: datetime):
        if self._data is None:
            self._data = pl.DataFrame(values)
        else:
            self._data.vstack(pl.DataFrame(values), in_place=True)
        self._times.append(pl.Series("time", [time]))

    def result(self) -> None | pl.DataFrame:
        if self._data is None:
            return None
        else:
            return self._data.rechunk().clone().with_columns(self._times)
