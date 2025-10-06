from datetime import datetime
from typing import Any, Protocol
import polars as pl


class Collector(Protocol):
    def collect(
        self,
        values: dict[str, float],
        control_mode: str | None,
        time: datetime,
    ): ...


class NullCollector(Collector):
    def collect(
        self,
        values: dict[str, float],
        control_mode: str | None,
        time: datetime,
    ):
        pass


class PolarsCollector(Collector):
    def __init__(self):
        self._data = None
        self._schema_overrides = None

    def collect(
        self,
        values: dict[str, Any],
        control_mode: str | None,
        time: datetime,
    ):
        if self._data is None:
            # Define schema overrides for known numeric columns
            self._schema_overrides = {
                "time": pl.Datetime(time_unit="us"),
                "control_mode": pl.String,
            }

            # Add Float64 for any column that looks numeric
            for key, value in values.items():
                if key.endswith("__bool"):
                    self._schema_overrides[key] = pl.Boolean
                else:
                    self._schema_overrides[key] = pl.Float64
            self._data = pl.DataFrame(
                {
                    **values,
                    "time": time,
                    "control_mode": control_mode,
                },
                schema_overrides=self._schema_overrides,
                strict=False,
            )
        else:
            self._data.vstack(
                pl.DataFrame(
                    {
                        **values,
                        "time": time,
                        "control_mode": control_mode,
                    },
                    schema_overrides=self._schema_overrides,
                    strict=False,
                ),
                in_place=True,
            )

    def result(self) -> None | pl.DataFrame:
        if self._data is None:
            return None
        else:
            return self._data.rechunk().clone()
