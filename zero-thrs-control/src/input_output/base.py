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

from input_output.definitions.units import unit_for_annotation
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


T = TypeVar("T")


class Stamped(ThrsModel, Generic[T]):
    value: T
    timestamp: datetime

    @staticmethod
    def stamp[V](value: V) -> "Stamped[V]":
        return Stamped(value=value, timestamp=datetime.now())


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


@dataclass
class Meta:
    yard_tag: str


class SimulationInputs(ThrsModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    def get_values_at_time(self, time: datetime) -> "SimulationInputs":
        def _component(component_name, component):
            component_value = getattr(self, component_name)

            def _field_type(field):
                return (Stamped[unit_for_annotation(field.annotation)], ...)

            def _field_value(field_name):
                value = getattr(component_value, field_name).value

                if isinstance(value, pl.DataFrame):
                    sorted_df = value.sort("time")
                    filtered_df = (
                        sorted_df.filter(sorted_df["time"] <= time)
                        .select("value")
                        .tail(1)
                    )

                    if (
                        sorted_df.select("time").tail(1).item() < time
                        or filtered_df.is_empty()
                    ):
                        raise ValueError(
                            f"Time {time} is outside the range of given data for field {component_name}."
                        )

                    return Stamped(value=filtered_df.item(), timestamp=time)
                else:
                    return Stamped(value=value, timestamp=time)

            fields = {
                field_name: _field_type(field)
                for field_name, field in component_value.model_fields.items()
            }
            model = create_model(
                str(component.annotation), __base__=component.annotation, **fields  # type: ignore
            )  # type: ignore
            values = {
                field_name: _field_value(field_name)
                for field_name in component_value.model_fields.keys()
            }
            return (model, ...), model(**values)

        components_with_values = {
            component_name: _component(component_name, component)
            for component_name, component in self.model_fields.items()
        }
        components = {
            component_name: component
            for component_name, (component, _) in components_with_values.items()
        }
        values = {
            component_name: value
            for component_name, (_, value) in components_with_values.items()
        }

        SelectedInputsModel = create_model(
            "SimulationInputs",
            __base__=SimulationInputs,
            **components,  # type: ignore
        )  # type: ignore

        return SelectedInputsModel(**values)
