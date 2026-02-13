"""
DBT model generator for sail system MQTT sources.

Generates flat RisingWave source tables (one per MQTT topic) that ingest
sail system PLC messages. Unlike the Marpower generator (which wraps fields
in a nested struct), sail system messages are flat JSON with PLC variable
names as keys.
"""

from pathlib import Path

from zero_data.io_list.types import IOTopic, IOValue
import logging

logger = logging.getLogger(__name__)


class SailSystemRawGenerator:
    def __init__(self, dbt_path: Path):
        self.table_path = dbt_path / "models/00_source/sail_system"

    def generate(self, topics: list[IOTopic]):
        """Generate a DBT source model for each sail system topic."""
        for topic in topics:
            file_name = self._table_name(topic.topic)
            content = self._generate_topic(topic)
            self._write_file(self.table_path, file_name, content)
            logger.info(f"Generated sail system source: {file_name}.sql")

    @classmethod
    def _write_file(cls, path: Path, file_name: str, content: str):
        file_path = (path / f"{file_name}.sql").resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)

    @staticmethod
    def _table_name(topic: str) -> str:
        """Derive table file name from MQTT topic (last path segment)."""
        return topic.split("/")[-1].replace("-", "_")

    @classmethod
    def _generate_topic(cls, topic: IOTopic) -> str:
        all_fields = [cls._timestamp()] + [cls._generate_field(f) for f in topic.fields]
        # Strip trailing comma from last field
        all_fields[-1] = all_fields[-1].rstrip(",\n") + "\n"
        fields = "".join(all_fields)
        return (
            "{{ config(materialized='table_with_connector') }}\n"
            "CREATE TABLE {{ this }} (\n"
            f"{fields}"
            ")\n"
            f"{cls._with_mqtt(topic.topic)}\n"
        )

    @staticmethod
    def _timestamp() -> str:
        return "\ttime TIMESTAMPTZ AS proctime(),\n"

    @staticmethod
    def _generate_field(io_value: IOValue) -> str:
        return f'\t"{io_value.name}"\t{io_value.data_type},\n'

    @staticmethod
    def _with_mqtt(topic: str) -> str:
        return f"{{{{ mqtt_with('{topic}') }}}}"
