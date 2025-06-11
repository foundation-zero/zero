from pathlib import Path
from typing import List

from io_processing.io_list.types import IOTopic, IOValue
import logging

logger = logging.getLogger(__name__)


class MarpowerRawGenerator:
    def __init__(self, dbt_path: Path):
        self.table_path = dbt_path / "models/raw/"
        self.sink_path = dbt_path / "sink/raw/"

    def generate(self, topics: List[IOTopic]):
        """Generate dbt models for the given topics."""
        for topic in topics:
            file_name = topic.topic.lower().replace("+", "_").replace(".", "_")
            table = self._generate_topic(topic)
            self._write_file(self.table_path, file_name, table)

            sink = self._generate_gcs_sink(topic)
            self._write_file(self.sink_path, f"{file_name}_gcs_sink", sink)

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
        timestamp = cls._add_timestamp()
        fields = "".join([cls._generate_field(io_val) for io_val in topic.fields])
        return f"{{{{ config(materialized='table_with_connector') }}}}\nCREATE TABLE {{{{ this }}}} (\n{timestamp}{fields})\n{with_mqtt}\n"

    @classmethod
    def _generate_gcs_sink(cls, topic: IOTopic) -> str:
        """Generate the SQL for a given sink."""
        topic_table = topic.topic.split("/")[-1]
        return f"{{{{ gcs_sink('raw', '{topic_table}', '{topic_table}_gcs_sink') }}}}"

    @staticmethod
    def _add_timestamp():
        """Generate the SQL for the timestamp."""
        return "\tTIMESTAMP\tTIMESTAMP,\n"

    @staticmethod
    def _generate_field(io_value: IOValue):
        """Generate the SQL for a given field."""
        return f"\t{io_value.name}\t{io_value.data_type},\n"

    @staticmethod
    def _with_mqtt(topic: str):
        """Generate the SQL for the MQTT connector."""
        return f"{{{{ mqtt_with('{topic}') }}}}"
