import json
from datetime import datetime
from io import StringIO

import polars as pl
import pytest
from pydantic import ValidationError

from input_output.base import SimulationInputs, Stamped, StampedDf


class SimpleInputs(SimulationInputs):
    a: Stamped[float]
    b: StampedDf[float]


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


def test_valid_inputs(valid_dataframe):
    inputs = SimpleInputs(a=Stamped.stamp(1.0), b=StampedDf.stamp(valid_dataframe))
    assert isinstance(inputs, SimpleInputs)
    assert inputs.a.value == 1.0
    assert inputs.b.value.equals(valid_dataframe)


def test_invalid_inputs():
    invalid_dataframe = pl.DataFrame({"value": [1, 2, 3]})

    with pytest.raises(ValidationError, match="DataFrame schema must be"):
        StampedDf.stamp(invalid_dataframe)


def test_inputs_selection(valid_dataframe):
    inputs = SimpleInputs(a=Stamped.stamp(1.0), b=StampedDf.stamp(valid_dataframe))

    values = inputs.get_values_at_time(datetime(2025, 1, 1)).model_dump()
    assert values["a"]["value"] == 1.0
    assert values["b"]["value"] == 1.0

    values = inputs.get_values_at_time(datetime(2025, 1, 2, hour=5)).model_dump()
    assert values["a"]["value"] == 1.0
    assert values["b"]["value"] == 2.0

    values = inputs.get_values_at_time(datetime(2025, 1, 3)).model_dump()
    assert values["a"]["value"] == 1.0
    assert values["b"]["value"] == 3.0

    with pytest.raises(ValueError, match="Time"):
        inputs.get_values_at_time(datetime(2024, 1, 1))

    with pytest.raises(ValueError, match="Time"):
        inputs.get_values_at_time(datetime(2026, 1, 1))
