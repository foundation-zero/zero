"""
DBT model generator for sail system MQTT sources.

Generates flat RisingWave source tables for sail system PLC messages.
Topics that share the same PLC struct type (group) are merged into a single
SQL file with a comma-separated topic subscription string, reducing duplication.
"""

from pathlib import Path
from collections import defaultdict

from zero_data.io_list.types import IOTopic, IOValue
import logging

logger = logging.getLogger(__name__)


class SailSystemRawGenerator:
    def __init__(self, dbt_path: Path):
        self.table_path = dbt_path / "models/00_source/sail_system"

    def generate(self, topics: list[IOTopic]):
        """Generate DBT source models, merging topics that share the same group."""
        # Group topics by their group key; ungrouped topics stay individual.
        groups: dict[str, list[IOTopic]] = defaultdict(list)
        for topic in topics:
            key = topic.group or topic.topic
            groups[key].append(topic)

        for key, group_topics in groups.items():
            file_name = self._group_filename(key, group_topics)
            content = self._generate_group(group_topics)
            self._write_file(self.table_path, file_name, content)
            topic_names = [t.topic for t in group_topics]
            logger.info(
                f"Generated sail system source: {file_name}.sql ({len(group_topics)} topics)"
            )
            logger.debug(f"  topics: {topic_names}")

    @classmethod
    def _write_file(cls, path: Path, file_name: str, content: str):
        file_path = (path / f"{file_name}.sql").resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)

    @staticmethod
    def _group_filename(key: str, group_topics: list[IOTopic]) -> str:
        """
        Derive a file name from the group key.

        If the key is a PLC struct type name (starts with 'T_'), strip the
        leading 'T_s' or 'T_' prefix and lowercase. Otherwise fall back to
        the per-topic naming used for ungrouped topics.
        """
        if key.startswith("T_"):
            name = key.removeprefix("T_s").removeprefix("T_")
            return name.lower()
        # Ungrouped topic — use the last path segment as before
        return key.split("/")[-1].replace("-", "_")

    @classmethod
    def _generate_group(cls, topics: list[IOTopic]) -> str:
        """Generate SQL for one or more topics with identical fields."""
        # All topics in a group share the same fields — take from the first.
        fields = topics[0].fields
        all_fields = [cls._timestamp()] + [cls._generate_field(f) for f in fields]
        all_fields[-1] = all_fields[-1].rstrip(",\n") + "\n"
        fields_sql = "".join(all_fields)

        topic_str = ",".join(t.topic for t in topics)
        return (
            "{{ config(materialized='table_with_connector') }}\n"
            "CREATE TABLE {{ this }} (\n"
            f"{fields_sql}"
            ")\n"
            f"{cls._with_mqtt(topic_str)}\n"
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
