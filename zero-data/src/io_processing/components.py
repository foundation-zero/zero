from functools import reduce
import json
from pathlib import Path

from polars import DataFrame
from yaml import load, Loader
import polars as pl
from jsonschema import validate

from io_processing.generated_components import Description, Type, Values
from io_processing.io_list import IoFlavor

_SUPPLIERS = {IoFlavor.AMCS: "marpower"}


class Components:
    def __init__(self, file: str) -> None:
        with open(Path(__file__).parent/"../../components.schema.json", "r") as f:
            _schema = json.load(f)
        with open(file, "r") as f:
            description = load(f, Loader=Loader)
            validate(description, schema=_schema)
            systems = description["systems"]
            components = [
                {"system": system["name"], **component}
                for system in systems
                for component in system["components"]
            ]

            self._components = DataFrame(components)
            self._description = Description(**description)

    def missing_components(self, io_list: DataFrame) -> DataFrame:
        return io_list.filter(pl.col("yard_tag").is_not_null()).join(
            self._components, left_on="yard_tag", right_on="tag", how="anti"
        )

    def orphan_signals(self, io_list: DataFrame) -> DataFrame:
        return io_list.filter(pl.col("yard_tag").is_null()).join(
            self._components, left_on="yard_tag", right_on="tag", how="anti"
        )

    def combine_with_value_name(self, io_list: DataFrame, flavor: IoFlavor):
        types = self._description.suppliers[_SUPPLIERS[flavor]].types

        # this constructs a big pl.when().then().when() with a when() for each value in each type
        def _component_replacer(expr, type: Type):
            def _value_replacer(expr, val: tuple[str, Values]):
                key, value = val
                return expr.when(
                    (pl.col("component_type") == type.id)
                    & (pl.col("tag").str.contains(value.name))
                    & (pl.col("type") == value.type)
                ).then(pl.lit(key))

            return reduce(_value_replacer, type.values.items(), expr)

        replace_expr = (
            reduce(_component_replacer, types, pl).otherwise(None).alias("value_name")
        )

        simple_components = self._components.select(
            pl.col("tag").alias("yard_tag"), pl.col("type").alias("component_type")
        )
        return (
            io_list.join(simple_components, on="yard_tag")
            .with_columns(replace_expr)
            .select(pl.exclude(["component_type"]))
        )

    def combine_io(self, io_list: DataFrame, flavor: IoFlavor) -> DataFrame:
        with_value_names = self.combine_with_value_name(io_list, flavor)
        io_to_signals = (
            with_value_names.select(
                "yard_tag", pl.struct(pl.exclude("yard_tag")).alias("signals")
            )
            .group_by("yard_tag")
            .all()
        )
        with_signals = self._components.join(
            io_to_signals, left_on="tag", right_on="yard_tag", coalesce=True
        )
        with_default_description = with_signals.with_columns(
            pl.when(
                pl.col("description").is_null() & (pl.col("signals").list.len() == 1)
            )
            .then(pl.col("signals").list[0].struct.field("description"))
            .otherwise(pl.col("description"))
        )
        return with_default_description
