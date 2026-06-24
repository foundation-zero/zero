from datetime import datetime
from typing import Any, Protocol

import polars as pl


class Collector[R](Protocol):
    def collect(
        self,
        values: dict[str, float],
        time: datetime,
    ): ...

    def result(self) -> R | None: ...


class PolarsCollector(Collector[pl.DataFrame]):
    _schema_overrides: dict[str, type[pl.DataType] | pl.DataType] | None

    def __init__(self):
        self._data = []
        self._schema_overrides = None

    def collect(
        self,
        values: dict[str, Any],
        time: datetime,
    ):
        self._data.append({**values, "time": time})

    def result(self) -> None | pl.DataFrame:
        if not self._data:
            return None

        all_keys = set().union(*(row.keys() for row in self._data))

        schema_overrides = {
            **{
                key: pl.Float64
                for key in all_keys
                if any(
                    key.endswith(s)
                    for s in [
                        "__C",
                        "__l_min",
                        "__ratio",
                        "__s",
                        "__Hz",
                        "__Bar",
                        "__Watt",
                    ]
                )
            },
            **{key: pl.Boolean for key in all_keys if key.endswith("__bool")},
            **{"time": pl.Datetime(time_unit="us")},
        }
        return pl.from_dicts(
            self._data,
            schema_overrides=schema_overrides,
            strict=False,
            infer_schema_length=None,
        )
