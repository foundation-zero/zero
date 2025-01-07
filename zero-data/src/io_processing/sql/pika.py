from dataclasses import dataclass, field
from typing import Any, Literal, Optional, Protocol
from pypika import (
    Table,
    Query,
    Field,
    AliasedQuery,
    Case,
    functions as fn,
    CustomFunction,
)
from pypika.queries import CreateQueryBuilder, Selectable
from pypika.terms import Term, Function
import pypika
import sqlparse

from pypika import Column


class Queryable(Protocol):
    def __str__(self) -> str: ...


@dataclass
class StructDef:
    fields: list[Column]

    def __str__(self):
        return f"""STRUCT <\n{",\n".join(str(field) for field in self.fields)}\n>"""

    def column(self, name: str) -> Column:
        return Column(name, str(self))


@dataclass
class Connector:
    pass


@dataclass
class MqttConnector(Connector):
    url: str
    topic: str
    qos: Literal["at_most_once", "at_least_once", "exactly_once"]
    username: str
    password: str
    encode: Literal["bytes", "json"]

    def __str__(self):
        return f"""(connector = 'mqtt',\nurl = '{self.url}',\ntopic = '{self.topic}',\nqos = '{self.qos}',\nusername = '{self.username}',\npassword = '{self.password}') FORMAT PLAIN ENCODE {self.encode.upper()}"""


@dataclass
class Include:
    column: str
    alias: Optional[str]

    def __str__(self):
        return (
            f"""INCLUDE {self.column} AS {self.alias}\n"""
            if self.alias
            else f"""INCLUDE {self.column}\n"""
        )


@dataclass
class CreateWithConnector:
    query: Query
    connector: Connector
    includes: list[Include] = field(default_factory=lambda: [])

    def __str__(self):
        return f"""{str(self.query)}\n{"\n".join(str(include) for include in self.includes)}WITH {str(self.connector)}"""


@dataclass
class Source:
    table_description: CreateQueryBuilder

    def __str__(self):
        return str(self.table_description).replace("CREATE TABLE", "CREATE SOURCE")


class Raw(Field):
    def get_sql(self, **kwargs):
        return super().get_sql(**{**kwargs, "quote_char": None})


@dataclass
class View:
    query: Selectable
    name: str
    materialized: bool

    def __str__(self) -> str:
        return f"""CREATE {'MATERIALIZED ' if self.materialized else ''}VIEW {self.name} AS {self.query.get_sql(quote_char=None)}"""


def create_view(query, name, materialized=False):
    return View(query, name, materialized)


def table_to_source(table: CreateQueryBuilder):
    return Source(table)


def source_with_connector(source, connector, includes):
    return CreateWithConnector(source, connector, includes)


def table_with_connector(table, connector, includes):
    return CreateWithConnector(table, connector, includes)


class GeneratedColumn(Column):
    # This abuses default as the generated column
    def __init__(self, name, type, function):
        super().__init__(name, type, default=function)

    def get_sql(self, **kwargs: Any) -> str:
        return super().get_sql(**kwargs).replace(" DEFAULT ", " AS ")


def proctime_col():
    return GeneratedColumn("timestamp", "TIMESTAMPTZ", proctime())


def data_col():
    return Column("data", "BYTEA")


_Tumble = CustomFunction("TUMBLE", ["table_or_source", "time_col", "window_size"])


@dataclass(eq=True, frozen=True)
class TumbleResult(Selectable):
    table: str | Selectable
    column: str | Field
    interval: str

    def get_sql(self, **kwargs):
        table = Field(self.table) if isinstance(self.table, str) else self.table
        col = Field(self.column) if isinstance(self.column, str) else self.column
        return _Tumble(table, col, Raw(f"INTERVAL '{self.interval}'")).get_sql(**kwargs)

    def get_table_name(self):
        return (
            self.table if isinstance(self.table, str) else self.table.get_table_name()
        )


def tumble(table, column, interval):
    return TumbleResult(table, column, interval)


class FirstValue(Function):
    def __init__(self, column, order_by, alias=None):
        super(FirstValue, self).__init__("FIRST_VALUE", alias=alias)
        self._column = column
        self._order_by = order_by

    def get_sql(self, **kwargs):
        col = Field(self._column) if isinstance(self._column, str) else self._column
        order = (
            Field(self._order_by) if isinstance(self._order_by, str) else self._order_by
        )
        alias = f" {self.alias}" if self.alias else ""
        return (
            f"FIRST_VALUE({col.get_sql(**kwargs)} ORDER BY {order.get_sql(**kwargs)})"
            + alias
        )


def first_value(column, order_by):
    return FirstValue(column, order_by)


ConvertFrom = CustomFunction("convert_from", ["string", "encoding"])

proctime = CustomFunction("PROCTIME")
