from typing import Any
from polars import DataFrame
import polars as pl
from pypika import Table, Query, Column, Case, functions as fns, Field
from pypika.terms import ValueWrapper
from io_processing.components import Components
from io_processing.generated_components import Description
import io_processing.sql.pika as io_pika

from io_processing.io_list import IoFlavor, find_type_description
from io_processing.utils.strings import snake_case

_IO_TOPICS = {IoFlavor.AMCS: "amcs/+"}
_IO_SOURCES = {IoFlavor.AMCS: "amcs"}

_SUPPLIERS = {IoFlavor.AMCS: "marpower"}

_signals = Table("signals")


def topic(signal_tag: str, flavor: IoFlavor) -> str:
    return _IO_TOPICS[flavor].replace("+", signal_tag)


def _source(flavor: IoFlavor) -> io_pika.Queryable:
    mqtt_connector = io_pika.MqttConnector(
        "mqtt://vernemq:1883",
        _IO_TOPICS[flavor],
        "at_least_once",
        "power-hub",
        "power-hub",
        "bytes",
    )

    source = io_pika.table_to_source(
        Query.create_table(_IO_SOURCES[flavor]).columns(
            io_pika.data_col(), io_pika.proctime_col()
        )
    )

    return io_pika.source_with_connector(
        source, mqtt_connector, [io_pika.Include("partition", "topic")]
    )


def _sql_type_for_type(type: str):
    match type:
        case "bool":
            return "BOOLEAN"
        case "f32":
            return "REAL"
        case "u32":
            return "BIGINT"
        case "i32":
            return "INTEGER"


def _materialized_view(
    description: Description, table_grouping: dict, flavor: IoFlavor
):
    type_description = find_type_description(
        table_grouping["type"], description.suppliers[_SUPPLIERS[flavor]]
    )
    table_name = f"{table_grouping["system"]}_{snake_case(table_grouping["type"])}s"
    topics_to_insert = [
        (topic(signal["tag"], flavor), component["tag"], signal["value_name"])
        for component in table_grouping["components"]
        for signal in component["signals"]
    ]
    inserts = Query.into(_signals).insert(*topics_to_insert)

    source = Table(_IO_SOURCES[flavor])

    pivotted_signals = Table("pivotted_signals")

    def _pivot_col(value_name, value):
        as_string = io_pika.ConvertFrom(source.data, ValueWrapper("utf-8"))
        cast = fns.Cast(as_string, _sql_type_for_type(value.type.value))
        return (
            Case()
            .when(_signals.value_name == value_name, cast)
            .else_(io_pika.Raw("NULL"))
        ).as_(value_name)

    pivot_cols = [
        _pivot_col(key, value) for key, value in type_description.values.items()
    ]

    pivot_query = (
        Query.from_(source)
        .join(_signals)
        .on(source.topic == _signals.topic)
        .select(source.timestamp, _signals.yard_tag, *pivot_cols)
    )

    value_cols = [
        io_pika.first_value(
            getattr(pivotted_signals, key),
            getattr(pivotted_signals, key),
        ).as_(key)
        for key in type_description.values.keys()
    ]

    return inserts, io_pika.create_view(
        (
            Query.with_(pivot_query, pivotted_signals.get_table_name())
            .from_(
                io_pika.tumble(
                    pivotted_signals, pivotted_signals.timestamp, "1 SECONDS"
                )
            )
            .as_(pivotted_signals)
            .select(
                Field("window_start"),
                Field("window_end"),
                pivotted_signals.yard_tag,
                *value_cols,
            )
            .groupby(
                Field("window_start"),
                Field("window_end"),
                pivotted_signals.yard_tag,
            )
        ),
        table_name,
        materialized=True,
    )


def sql_for_io(description: Description, components: DataFrame, flavor: IoFlavor):
    topic = Column("topic", "VARCHAR")
    signals = (
        Query.create_table(_signals)
        .columns(topic, Column("yard_tag", "VARCHAR"), Column("value_name", "VARCHAR"))
        .primary_key(topic)
    )

    table_groupings = (
        components.with_columns(
            pl.col("signals")
            .list.eval(pl.element().struct.field("value_name"))
            .alias("value_names")
        )
        .select(
            pl.col("system"),
            pl.col("type"),
            pl.struct(pl.exclude("system", "type")).alias("components"),
        )
        .group_by([pl.col("system"), pl.col("type")])
        .agg(pl.col("components"))
        .iter_rows(named=True)
    )

    return (
        _source(flavor),
        signals,
        {
            f"{tg["system"]}_{snake_case(tg["type"])}": _materialized_view(
                description, tg, flavor
            )
            for tg in table_groupings
        },
    )
