import json
from datetime import datetime
from io import StringIO

import polars as pl
import pytest
from pydantic import ValidationError

from simulation.input_output import SimulationInputs


class SimpleInputs(SimulationInputs):
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


def test_valid_inputs(valid_dataframe):
    inputs = SimpleInputs(a=1.0, b=valid_dataframe)
    assert isinstance(inputs, SimpleInputs)
    assert inputs.a == 1.0
    assert inputs.b.equals(valid_dataframe)


def test_invalid_inputs(valid_dataframe):
    invalid_dataframe = pl.DataFrame({"value": [1, 2, 3]})

    with pytest.raises(ValidationError, match="DataFrame schema must be"):
        SimpleInputs(a=1.0, b=invalid_dataframe)

    with pytest.raises(ValidationError, match="Fields must be"):
        SimpleInputs(a="hello", b=valid_dataframe)  # type: ignore


def test_inputs_selection(valid_dataframe):
    inputs = SimpleInputs(a=1.0, b=valid_dataframe)

    assert inputs.get_values_at_time(datetime(2025, 1, 1)).model_dump() == {
        "a": 1.0,
        "b": 1.0,
    }
    assert inputs.get_values_at_time(datetime(2025, 1, 2, hour=5)).model_dump() == {
        "a": 1.0,
        "b": 2.0,
    }
    assert inputs.get_values_at_time(datetime(2025, 1, 3)).model_dump() == {
        "a": 1.0,
        "b": 3.0,
    }

    with pytest.raises(ValueError, match="Time"):
        inputs.get_values_at_time(datetime(2024, 1, 1))

    with pytest.raises(ValueError, match="Time"):
        inputs.get_values_at_time(datetime(2026, 1, 1))


def test_environmentals_serialization(valid_dataframe):
    siumlation_inputs = SimpleInputs(a=1.0, b=valid_dataframe)
    serialized = siumlation_inputs.model_dump_json()
    model_dict = json.loads(serialized)
    assert model_dict["a"] == 1.0
    assert pl.read_json(
        StringIO(model_dict["b"]), schema=valid_dataframe.schema
    ).equals(valid_dataframe)
