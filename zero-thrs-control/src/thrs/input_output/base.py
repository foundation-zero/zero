from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any, Literal, Self
from warnings import warn

import polars as pl
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    create_model,
    field_validator,
)
from pydantic.alias_generators import to_pascal
from pydantic.fields import FieldInfo
from thrs.input_output.definitions.units import (
    PcsMode,
    unit_for_annotation,
    zero_for_unit,
)


class ThrsValues(BaseModel):
    """ThrsValues provides the conversion between the camel case in MQTT messages to Python underscores"""

    model_config = ConfigDict(
        alias_generator=to_pascal,
        use_enum_values=True,
        validate_by_name=True,
    )

    @classmethod
    def zero(cls) -> Self:
        def _zero_component(component):
            def _zero_value(field: FieldInfo):
                unit = unit_for_annotation(field.annotation)
                return zero_for_unit(unit) if unit else 0.0

            if issubclass(component, ThrsValues):
                return component(
                    **{
                        field_name: Stamped.stamp(_zero_value(field))
                        for field_name, field in component.model_fields.items()
                    }
                )
            else:
                unit = unit_for_annotation(component)
                return zero_for_unit(unit) if unit else 0.0

        vals = {
            component_name: _zero_component(component.annotation)
            for component_name, component in cls.model_fields.items()
        }
        return cls(**vals)


class Stamped[T](ThrsValues):
    value: T
    timestamp: Annotated[datetime, Field(alias="TimeStamp")]

    @staticmethod
    def stamp[V](value: V) -> "Stamped[V]":
        return Stamped(value=value, timestamp=datetime.now())


class StampedDf[T](ThrsValues):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    value: pl.DataFrame

    @field_validator("value", mode="before")
    def validate_field(cls, value):
        if isinstance(value, pl.DataFrame):
            expected_schema = [
                {"time": pl.Datetime(time_unit="us", time_zone=None), "value": type}
                for type in [
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


class ComponentMeta(BaseModel):
    yard_tag: str = ""
    included_in_fmu: bool = True
    component_type: str | None = None
    valve_type: Literal["shutoff", "switch", "mix", "flowcontrol"] | None = None


def component_meta(*args, **kwargs):
    return Field(json_schema_extra=ComponentMeta(*args, **kwargs).model_dump())


@dataclass
class ParameterMeta:
    fds_tag: str


class FieldMeta(BaseModel):
    included_in_fmu: bool = True


def field_meta(*args, **kwargs):
    return Field(json_schema_extra=FieldMeta(*args, **kwargs).model_dump())


_dedataframed_dataclasses = {}


class SimulationValues(ThrsValues):
    @classmethod
    def dedataframe(cls) -> type:
        def _component(component_name, component):
            if stored := _dedataframed_dataclasses.get(component.annotation, None):
                return stored

            def _field_type(field):
                if field.json_schema_extra:
                    info = FieldInfo.from_annotation(
                        Annotated[
                            Stamped[unit_for_annotation(field.annotation)],
                            Field(json_schema_extra=field.json_schema_extra),
                        ]  # type: ignore
                    )
                    return Annotated[
                        Stamped[unit_for_annotation(field.annotation)], info
                    ]

                else:
                    return (Stamped[unit_for_annotation(field.annotation)], ...)

            fields = {
                field_name: _field_type(field)
                for field_name, field in component.annotation.model_fields.items()
            }
            model = create_model(
                str(component.annotation.__name__),
                __base__=component.annotation,
                **fields,  # type: ignore
            )  # type: ignore
            _dedataframed_dataclasses[component.annotation] = (model, ...)
            return (model, ...)

        def _component_with_metadata(component_name, component):
            dedataframed_component = _component(component_name, component)
            # Preserve the original field metadata (like included_in_fmu) from the parent class
            if component.json_schema_extra:
                info = FieldInfo.from_annotation(
                    Annotated[
                        dedataframed_component[0]
                        if isinstance(dedataframed_component, tuple)
                        else dedataframed_component,
                        Field(json_schema_extra=component.json_schema_extra),
                    ]  # type: ignore
                )
                return Annotated[
                    dedataframed_component[0]
                    if isinstance(dedataframed_component, tuple)
                    else dedataframed_component,
                    info,
                ]
            else:
                return dedataframed_component

        components = {
            component_name: _component_with_metadata(component_name, component)
            for component_name, component in cls.model_fields.items()
        }

        SelectedInputsModel = create_model(
            cls.__name__,
            __base__=SimulationValues,
            **components,  # type: ignore
        )  # type: ignore

        return SelectedInputsModel


class SimulationInputs(SimulationValues):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    def get_values_at_time(self, time: datetime) -> Self:
        SelectedInputsModel = self.dedataframe()

        def _component(component_name, component):
            component_value = getattr(self, component_name)

            def _field_value(field_name):
                value = getattr(component_value, field_name).value

                if isinstance(value, pl.DataFrame):
                    if value.select(pl.min("time")).item() > time:
                        warn(
                            f"Time {time} is before the given range of data for field {component_name}."
                        )

                        return Stamped(
                            value=value.sort("time").head(1).select("value").item(),
                            timestamp=time,
                        )

                    if value.select(pl.max("time")).item() < time:
                        warn(
                            f"Time {time} is after the given range of data for field {component_name}."
                        )

                        return Stamped(
                            value=value.sort("time").tail(1).select("value").item(),
                            timestamp=time,
                        )

                    else:
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

                else:
                    return Stamped(value=value, timestamp=time)

            values = {
                field_name: _field_value(field_name)
                for field_name in type(component_value).model_fields.keys()
            }
            return SelectedInputsModel.model_fields[component_name].annotation(**values)

        values = {
            component_name: _component(component_name, component)
            for component_name, component in type(self).model_fields.items()
        }

        return SelectedInputsModel(**values)


@dataclass
class CombinedValues:
    values: dict[str, ThrsValues]
