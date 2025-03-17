import polars as pl


class Collector:
    def __init__(self):
        self._data = None

    def collect(self, values: dict[str, float]):
        if self._data is None:
            self._data = pl.DataFrame(values)
        else:
            self._data.vstack(pl.DataFrame(values), in_place=True)

    def result(self) -> None | pl.DataFrame:
        if self._data is None:
            return None
        else:
            return self._data.rechunk().clone()
