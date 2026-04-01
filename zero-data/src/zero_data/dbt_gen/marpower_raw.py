from pathlib import Path
from typing import List

from zero_data.io_list.types import IOTopic, IOValue
from zero_data.utils import detect_same_format


class MarpowerRawGenerator:
    def __init__(self, dbt_path: Path):
        self.table_path = dbt_path / "models/00_source/"
        self.sink_path = dbt_path / "models/40_sinks/"

    def generate(self, topics: List[IOTopic]):
        """Generate dbt models for the given topics."""

        unnested, squashed, unsquashed = detect_same_format(topics)
        for topic in unnested + squashed + unsquashed:
            file_name = self._table(topic.topic.removeprefix("marpower/"))
            table = self._generate_topic(topic)
            self._write_file(self.table_path, file_name, table)

    @classmethod
    def _write_file(cls, path: Path, file_name: str, content: str):
        """Write the content to a file."""
        file_path = (path / f"{file_name}.sql").resolve()

        # Ensure folder exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as f:
            f.write(content)

    @classmethod
    def _generate_topic(cls, topic: IOTopic) -> str:
        """Generate the SQL for a given topic."""
        with_mqtt = cls._with_mqtt(topic.topic)
        fields = "".join([cls._generate_field(io_val) for io_val in topic.fields])
        return f"{{{{ config(materialized='table_with_connector') }}}}\nCREATE TABLE {{{{ this }}}} (\n{cls._timestamp()}{fields})\n{cls._include_topic()}{with_mqtt}\n"

    @classmethod
    def _generate_gcs_sink(cls, topic: IOTopic) -> str:
        """Generate the SQL for a given sink."""
        topic_table = cls._table(topic.topic)
        return (
            f"{{{{ sink_append_gcs('raw', '{topic_table}', '{topic_table}_sink') }}}}"
        )

    @staticmethod
    def _table(topic: str) -> str:
        """Generate the table name for a topic."""
        return f"marpower/{topic.removeprefix('marpower/').replace('/', '_').replace('-', '_').rstrip('#_')}"

    @staticmethod
    def _timestamp() -> str:
        """Generate the SQL for the timestamp field."""
        return "\ttime TIMESTAMPTZ AS proctime(),\n"

    @staticmethod
    def _generate_field(io_value: IOValue):
        """Generate the SQL for a given field."""
        return f'\t"{io_value.name.replace(" ", "")}"\t{{{{ marpower_struct("{io_value.data_type}") }}}},\n'

    @staticmethod
    def _include_topic():
        return "INCLUDE partition AS topic\n"

    @staticmethod
    def _with_mqtt(topic: str):
        """Generate the SQL for the MQTT connector."""
        return f"{{{{ mqtt_with('{topic}') }}}}"
