from datetime import datetime

import polars as pl
from pydantic import (BaseModel, ConfigDict, create_model, field_serializer,
                      field_validator)


class SimulationInputs(BaseModel):

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @field_serializer("*", mode="plain", when_used="json")
    def serialize_field(value):
        if isinstance(value, float):
            return value
        elif isinstance(value, pl.DataFrame):
            return value.write_json()

    @field_validator("*", mode="before")
    def validate_field(cls, value):
        if isinstance(value, pl.DataFrame):
            expected_schema = {
                "time": pl.Datetime(time_unit="us", time_zone=None),
                "value": pl.Float64,
            }
            if value.schema != expected_schema:
                raise ValueError(
                    f"DataFrame schema must be {expected_schema}, got {value.schema}"
                )
        elif not isinstance(value, float):
            raise ValueError(
                "Fields must be either a float or a Polars DataFrame with 'time' (Datetime) and 'value' (Float64)."
            )
        return value

    def get_values_at_time(self, time: datetime) -> "SimulationInputs":
        result = {}
        for field_name in self.model_fields:
            value = getattr(self, field_name)

            if isinstance(value, pl.DataFrame):
                sorted_df = value.sort("time")
                filtered_df = (
                    sorted_df.filter(sorted_df["time"] <= time).select("value").tail(1)
                )

                if (
                    sorted_df.select("time").tail(1).item() < time
                    or filtered_df.is_empty()
                ):
                    raise ValueError(
                        f"Time {time} is outside the range of given data for field {field_name}."
                    )
                else:
                    result[field_name] = filtered_df.item()
            else:
                result[field_name] = value

        SelectedInputsModel = create_model(
            "SimulationInputs",
            __base__=SimulationInputs,
            **{field_name: (float, ...) for field_name in result.keys()},  # type: ignore
        )  # type: ignore

        return SelectedInputsModel(**result)
