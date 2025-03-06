import json
from datetime import datetime
from io import StringIO

import polars as pl
import pytest
from pydantic import ValidationError

from simulation.environmentals import Environmentals


class SimpleEnvironmentals(Environmentals):
    a: float
    b: pl.DataFrame


@pytest.fixture
def valid_dataframe():
    return pl.DataFrame(
        {
            "time": pl.datetime_range(
                datetime(2025, 1, 1), datetime(2025, 1, 3), interval="1d", eager=True
            ),
            "value": pl.Series([1.0, 2.0, 3.0], dtype=pl.Float64),
        }
    )


def test_valid_environmentals(valid_dataframe):
    environmentals = SimpleEnvironmentals(a=1.0, b=valid_dataframe)
    assert isinstance(environmentals, SimpleEnvironmentals)
    assert environmentals.a == 1.0
    assert environmentals.b.equals(valid_dataframe)


def test_invalid_environmentals(valid_dataframe):
    invalid_dataframe = pl.DataFrame({"value": [1, 2, 3]})

    with pytest.raises(ValidationError, match="DataFrame schema must be"):
        SimpleEnvironmentals(a=1.0, b=invalid_dataframe)

    with pytest.raises(ValidationError, match="Fields must be"):
        SimpleEnvironmentals(a="hello", b=valid_dataframe)  # type: ignore


def test_environmentals_selection(valid_dataframe):
    environmentals = SimpleEnvironmentals(a=1.0, b=valid_dataframe)

    assert environmentals.get_values_at_time(datetime(2025, 1, 1)) == {
        "a": 1.0,
        "b": 1.0,
    }
    assert environmentals.get_values_at_time(datetime(2025, 1, 2, hour=5)) == {
        "a": 1.0,
        "b": 2.0,
    }
    assert environmentals.get_values_at_time(datetime(2025, 1, 3)) == {
        "a": 1.0,
        "b": 3.0,
    }

    with pytest.raises(ValueError, match="Time"):
        environmentals.get_values_at_time(datetime(2024, 1, 1))

    with pytest.raises(ValueError, match="Time"):
        environmentals.get_values_at_time(datetime(2026, 1, 1))


def test_environmentals_serialization(valid_dataframe):
    environmentals = SimpleEnvironmentals(a=1.0, b=valid_dataframe)
    serialized = environmentals.model_dump_json()
    model_dict = json.loads(serialized)
    assert model_dict["a"] == 1.0
    assert pl.read_json(
        StringIO(model_dict["b"]), schema=valid_dataframe.schema
    ).equals(valid_dataframe)
