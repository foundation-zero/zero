import pytest

from zero_data.dbt_gen import SailSystemRawGenerator
from zero_data.io_list.types import IOTopic, IOValue


def test_generate(tmp_path):
    topic_name = "test_topic"
    io_topics = [
        IOTopic(topic_name, [IOValue("field1", "bool"), IOValue("field2", "f32")])
    ]
    dbt_dir = tmp_path / "dbt"
    dbt_dir.mkdir()
    SailSystemRawGenerator(dbt_dir).generate(io_topics)

    with open(dbt_dir / f"models/00_source/sail_system/{topic_name}.sql") as f:
        sql = f.read()

    assert (
        sql
        == """{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
\ttime TIMESTAMPTZ AS proctime(),
\t"field1"\tbool,
\t"field2"\tf32
)
{{ mqtt_with('%s') }}
"""
        % topic_name
    )


def test_generate_grouped(tmp_path):
    topic_group_name = "test_group"
    topic_name_1 = "topic1"
    topic_name_2 = "topic2"
    io_topics = [
        IOTopic(
            topic_name_1,
            [IOValue("field1", "bool"), IOValue("field2", "f32")],
            topic_group_name,
        ),
        IOTopic(
            topic_name_2,
            [IOValue("field3", "bool"), IOValue("field4", "f32")],
            topic_group_name,
        ),
    ]
    dbt_dir = tmp_path / "dbt"
    dbt_dir.mkdir()
    print(dbt_dir)
    SailSystemRawGenerator(dbt_dir).generate(io_topics)

    with open(dbt_dir / f"models/00_source/sail_system/{topic_group_name}.sql") as f:
        sql = f.read()

    assert (
        sql
        == """{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
\ttime TIMESTAMPTZ AS proctime(),
\t"field1"\tbool,
\t"field2"\tf32
)
{{ mqtt_with('%s,%s') }}
"""
        % (topic_name_1, topic_name_2)
    )


@pytest.mark.parametrize("prefix", ["T_", "T_s"])
def test_strip_group_prefix(tmp_path, prefix):
    group_name = "test_group"
    topic_group_name = prefix + group_name
    topic_name_1 = "topic1"
    topic_name_2 = "topic2"
    io_topics = [
        IOTopic(
            topic_name_1,
            [IOValue("field1", "bool"), IOValue("field2", "f32")],
            topic_group_name,
        ),
        IOTopic(
            topic_name_2,
            [IOValue("field3", "bool"), IOValue("field4", "f32")],
            topic_group_name,
        ),
    ]
    dbt_dir = tmp_path / "dbt"
    dbt_dir.mkdir()
    print(dbt_dir)
    SailSystemRawGenerator(dbt_dir).generate(io_topics)

    with open(dbt_dir / f"models/00_source/sail_system/{group_name}.sql") as f:
        sql = f.read()

    assert (
        sql
        == """{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
\ttime TIMESTAMPTZ AS proctime(),
\t"field1"\tbool,
\t"field2"\tf32
)
{{ mqtt_with('%s,%s') }}
"""
        % (topic_name_1, topic_name_2)
    )
