from datetime import datetime
from typing import Any, Protocol
import polars as pl


class Collector(Protocol):
    def collect(self, values: dict[str, float], control_mode: str | None, time: datetime): ...


class NullCollector(Collector):
    def collect(self, values: dict[str, float], control_mode: str | None, time: datetime):
        pass


class PolarsCollector(Collector):
    def __init__(self):
        self._data = None

    def collect(self, values: dict[str, Any], control_mode: str | None, time: datetime):
        if self._data is None:
            self._data = pl.DataFrame({**values, 'time': time, 'control_mode': control_mode})
            self._data = self._data.with_columns(pl.col('time').cast(pl.Datetime), pl.col('control_mode').cast(pl.Categorical))
            self._schema = self._data.schema
        else:
            self._data.vstack(pl.DataFrame({**values, 'time': time, 'control_mode': control_mode}, schema_overrides = self._schema, strict = False), in_place=True)

    def result(self) -> None | pl.DataFrame:
        if self._data is None:
            return None
        else:
            return self._data.rechunk().clone()
