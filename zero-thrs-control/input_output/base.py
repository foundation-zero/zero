from dataclasses import dataclass
from datetime import datetime
from typing import Any, Generic, Self, TypeVar

import polars as pl
from pydantic import (
    AliasGenerator,
    BaseModel,
    ConfigDict,
    create_model,
    field_validator,
)

from utils.string import hyphenize


class ThrsModel(BaseModel):
    """ThrsModel provides the conversion between the dashes in MQTT to Python underscores"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=hyphenize,
        )
    )

    @classmethod
    def zero(cls) -> Self:
        def _zero_component(component):
            return component(
                **{
                    field_name: Stamped.stamp(0.0)
                    for field_name in component.model_fields.keys()
                }
            )

        vals = {
            component_name: _zero_component(component.annotation)
            for component_name, component in cls.model_fields.items()
        }
        return cls(**vals)


def _unit_for_stamp(annotation):
    return next(iter(annotation.__pydantic_generic_metadata__["args"]), None)  # type: ignore


T = TypeVar("T")


class Stamped(ThrsModel, Generic[T]):
    value: T
    timestamp: datetime

    @staticmethod
    def stamp[V](value: V) -> "Stamped[V]":
        return Stamped(value=value, timestamp=datetime.now())

    @classmethod
    def unit(cls) -> Any:
        return _unit_for_stamp(cls)


T2 = TypeVar("T2")


class StampedDf(ThrsModel, Generic[T2]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    value: pl.DataFrame

    @field_validator("value", mode="before")
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

    @staticmethod
    def stamp(value: pl.DataFrame) -> "StampedDf[Any]":
        return StampedDf(value=value)

    @classmethod
    def unit(cls) -> Any:
        return _unit_for_stamp(cls)


@dataclass
class Meta:
    yard_tag: str


class SimulationInputs(ThrsModel):

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    def get_values_at_time(self, time: datetime) -> "SimulationInputs":
        values = {}
        fields = {}
        for field_name, field in self.model_fields.items():
            unit = field.annotation.unit()  # type: ignore
            value = getattr(self, field_name).value

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
                    values[field_name] = Stamped(
                        value=filtered_df.item(), timestamp=time
                    )
                    fields[field_name] = unit
            else:
                values[field_name] = Stamped(value=value, timestamp=time)
                fields[field_name] = unit

        SelectedInputsModel = create_model(
            "SimulationInputs",
            __base__=SimulationInputs,
            **{field_name: (Stamped[unit], ...) for field_name, unit in fields.items()},  # type: ignore
        )  # type: ignore

        return SelectedInputsModel(**values)
