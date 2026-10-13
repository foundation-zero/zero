from datetime import datetime
from typing import Annotated

import polars as pl
import pytest
from pydantic import ValidationError

from analysis.simulation_values import StampedDf, dataframify
from thrs.input_output.base import Stamped, ThrsValues, field_meta
from thrs.input_output.definitions.simulation import HeatSource
from thrs.input_output.definitions.units import Ratio, Watt, unit_for_annotation


class SimpleInputs(ThrsValues):
    a: HeatSource
    b: Annotated[HeatSource, field_meta(included_in_fmu=False)]


SimpleInputsDf = dataframify(SimpleInputs)


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


def test_dataframe():
    assert dataframify(Stamped[Watt]) == Stamped[Watt] | StampedDf[Watt]
    assert (
        dataframify(HeatSource).model_fields["heat_flow"].annotation
        == Stamped[Watt] | StampedDf[Watt]
    )
    assert (
        dataframify(SimpleInputs)
        .model_fields["a"]
        .annotation.model_fields["heat_flow"]
        .annotation
        == Stamped[Watt] | StampedDf[Watt]
    )
    assert (
        dataframify(SimpleInputs)
        .model_fields["b"]
        .annotation.model_fields["heat_flow"]
        .annotation
        == Stamped[Watt] | StampedDf[Watt]
    )
    assert dataframify(SimpleInputs).model_fields["a"].json_schema_extra is None
    assert dataframify(SimpleInputs).model_fields["b"].json_schema_extra == {
        "included_in_fmu": False
    }


def test_valid_inputs(valid_dataframe):
    inputs = SimpleInputsDf(
        a={"heat_flow": Stamped.stamp(1.0)},
        b={"heat_flow": StampedDf.stamp(valid_dataframe)},
    )
    assert isinstance(inputs, SimpleInputsDf)
    assert isinstance(inputs.a.heat_flow.value, float)
    assert inputs.a.heat_flow.value == 1.0
    assert isinstance(inputs.b.heat_flow.value, pl.DataFrame)
    assert inputs.b.heat_flow.value.equals(valid_dataframe)


def test_invalid_inputs():
    invalid_dataframe = pl.DataFrame({"value": [1, 2, 3]})

    with pytest.raises(ValidationError, match="DataFrame schema must be"):
        StampedDf.stamp(invalid_dataframe)


def test_inputs_selection(valid_dataframe):
    inputs = SimpleInputsDf(
        a={"heat_flow": Stamped.stamp(1.0)},
        b={"heat_flow": StampedDf.stamp(valid_dataframe)},
    )

    values = inputs.get_values_at_time(datetime(2025, 1, 1)).model_dump()
    assert values["a"]["heat_flow"]["value"] == 1.0
    assert values["b"]["heat_flow"]["value"] == 1.0

    values = inputs.get_values_at_time(datetime(2025, 1, 2, hour=5)).model_dump()
    assert values["a"]["heat_flow"]["value"] == 1.0
    assert values["b"]["heat_flow"]["value"] == 2.0

    values = inputs.get_values_at_time(datetime(2025, 1, 3)).model_dump()
    assert values["a"]["heat_flow"]["value"] == 1.0
    assert values["b"]["heat_flow"]["value"] == 3.0

    with pytest.warns(match="Time"):
        values = inputs.get_values_at_time(datetime(2024, 1, 1)).model_dump()
        assert values["a"]["heat_flow"]["value"] == 1.0
        assert values["b"]["heat_flow"]["value"] == 1.0

    with pytest.warns(match="Time"):
        values = inputs.get_values_at_time(datetime(2026, 1, 1)).model_dump()
        assert values["a"]["heat_flow"]["value"] == 1.0
        assert values["b"]["heat_flow"]["value"] == 3.0


def test_unit_for_annotation_stamped_df():
    class Data(ThrsValues):
        a: StampedDf[Ratio]

    assert unit_for_annotation(Data.model_fields["a"].annotation) == Ratio


def test_unit_for_annotation_union():
    class Data(ThrsValues):
        a: Stamped[Ratio] | StampedDf[Ratio]

    assert unit_for_annotation(Data.model_fields["a"].annotation) == Ratio
