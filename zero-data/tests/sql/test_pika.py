from io_processing.sql.pika import create_view, tumble, first_value
from pypika import Query, Table


def test_tumble():
    assert "TUMBLE(test,time_column,INTERVAL '10 SECONDS')" == tumble(
        "test", "time_column", "10 SECONDS"
    ).get_sql(quote_char=None)


def test_tumble_in_query():
    assert (
        """SELECT * FROM TUMBLE("table","time_column",INTERVAL '10 SECONDS')"""
        == Query.from_(tumble("table", "time_column", "10 SECONDS"))
        .select("*")
        .get_sql()
    )


def test_tumble_field():
    assert '"table"."column"' == tumble("table", "time_column", "10 SECONDS").field(
        "column"
    )


def test_tumble_table():
    table = Table("table")
    assert (
        """SELECT * FROM TUMBLE("table","time_column",INTERVAL '10 SECONDS')"""
        == Query.from_(tumble(table, table.time_column, "10 SECONDS"))
        .select("*")
        .get_sql()
    )


def test_first_value():
    assert "FIRST_VALUE(column ORDER BY time)" == first_value("column", "time").get_sql(
        quote_char=None
    )


def test_first_value_in_query():
    table = Table("table")
    assert (
        'SELECT FIRST_VALUE("column" ORDER BY "time_column") FROM "table"'
        == Query.from_(table)
        .select(first_value(table.column, table.time_column))
        .get_sql()
    )


def test_create_view():
    assert "CREATE VIEW view AS SELECT * FROM table" == str(
        create_view(Query.from_("table").select("*"), "view")
    )


def test_create_materialized_view():
    assert "CREATE MATERIALIZED VIEW view AS SELECT * FROM table" == str(
        create_view(Query.from_("table").select("*"), "view", materialized=True)
    )
