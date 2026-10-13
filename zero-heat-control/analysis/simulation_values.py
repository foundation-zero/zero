from datetime import datetime
from inspect import isclass
from typing import Annotated, Any, Self
from warnings import warn

import polars as pl
from pydantic import ConfigDict, Field, create_model, field_validator
from pydantic.fields import FieldInfo

from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.units import PcsMode, unit_for_annotation


class StampedDf[T](ThrsValues):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    value: pl.DataFrame | float

    @field_validator("value", mode="before")
    @classmethod
    def validate_field(cls, value):
        if isinstance(value, pl.DataFrame):
            expected_schema = [
                {
                    "time": pl.Datetime(time_unit="us", time_zone=None),
                    "value": dataframe_type,
                }
                for dataframe_type in [
                    pl.Float64,
                    pl.Int64,
                    pl.Boolean,
                    pl.String,
                    pl.Enum(PcsMode),
                ]
            ]
            if value.schema not in expected_schema:
                raise ValueError(
                    f"DataFrame schema must be in {expected_schema}, got {value.schema}"
                )
        elif not isinstance(value, float):
            raise ValueError(
                "Fields must be either a float or a Polars DataFrame with 'time' (Datetime) and 'value' (Float64)."
            )
        return value

    @staticmethod
    def stamp(value: pl.DataFrame) -> "StampedDf[Any]":
        return StampedDf(value=value)


class SimulationValues(ThrsValues):
    def get_values_at_time(self, time: datetime) -> Self:
        SelectedInputsModel = self.__class__.original  # type: ignore  # noqa: N806

        def _component(component_name, component):
            component_value = getattr(self, component_name)

            def _field_value(field_name):
                value = getattr(component_value, field_name).value

                if isinstance(value, pl.DataFrame):
                    if value.select(pl.min("time")).item() > time:
                        warn(
                            f"Time {time} is before the given range of data for field {component_name}.",
                            stacklevel=1,
                        )

                        return Stamped(
                            value=value.sort("time").head(1).select("value").item(),
                            timestamp=time,
                        )

                    if value.select(pl.max("time")).item() < time:
                        warn(
                            f"Time {time} is after the given range of data for field {component_name}.",
                            stacklevel=1,
                        )

                        return Stamped(
                            value=value.sort("time").tail(1).select("value").item(),
                            timestamp=time,
                        )

                    return Stamped(
                        value=value.filter(
                            (m := (pl.col("time") - time).abs())
                            .filter(pl.col("time") <= time)
                            .min()
                            == m
                        )
                        .limit(1)
                        .select("value")
                        .item(),
                        timestamp=time,
                    )

                return Stamped(value=value, timestamp=time)

            values = {
                field_name: _field_value(field_name)
                for field_name in type(component_value).model_fields
            }
            return SelectedInputsModel.model_fields[component_name].annotation(**values)

        values = {
            component_name: _component(component_name, component)
            for component_name, component in type(self).model_fields.items()
        }

        return SelectedInputsModel(**values)


_dataframed_dataclasses = {}


def _component_with_metadata(field, component):
    # Preserve the original field metadata (like included_in_fmu) from the parent class
    if getattr(field, "json_schema_extra", None):
        info = FieldInfo.from_annotation(
            Annotated[
                component,
                Field(json_schema_extra=field.json_schema_extra),
            ]  # type: ignore
        )
        return Annotated[component, info]
    return component


def dataframify(cls: type[ThrsValues]) -> type:
    if stored := _dataframed_dataclasses.get(cls):
        return stored

    if isclass(cls) and issubclass(cls, Stamped):
        field_type = unit_for_annotation(cls)

        return Stamped[field_type] | StampedDf[field_type]  # type: ignore

    components = {
        component_name: _component_with_metadata(
            component,
            dataframify(component.annotation),  # type: ignore
        )
        for component_name, component in cls.model_fields.items()
    }

    methods = {
        method_name: getattr(cls, method_name)
        for method_name in cls.model_computed_fields
    }

    model = create_model(  # type: ignore
        f"{cls.__name__!s}Df",
        __base__=SimulationValues,
        __validators__=methods,
        **components,  # type: ignore
    )

    _dataframed_dataclasses[cls] = model
    model.original = cls
    return model
