import os
import glob
from pathlib import Path
from typing import List

from io_processing.io_list.types import IOTopic, IOValue
import logging

logger = logging.getLogger(__name__)


class MarpowerRawGenerator:
    def __init__(self, dbt_path: Path):
        self.dbt_path = dbt_path / "models/raw/"

    def generate(self, topics: List[IOTopic]):
        """Generate dbt models for the given topics."""
        number_of_files_removed = self._clean_folder()
        for topic in topics:
            file_name = topic.topic.lower()
            # Create subfolders for nested topics
            subfolder_path = self.dbt_path / file_name.rsplit("/", 1)[0]
            subfolder_path.mkdir(parents=True, exist_ok=True)

            file_path = (self.dbt_path / f"{file_name}.sql").resolve()
            table = self._generate_topic(topic)
            with open(file_path, "w") as f:
                f.write(table)
        number_of_new_files = len(topics)
        logger.info(f"Written raw tables to {self.dbt_path.resolve()}")
        logger.info(
            f"""
            Created: {number_of_new_files}
            Removed: {number_of_files_removed}
            Delta: {number_of_new_files - number_of_files_removed}"""
        )

    def _clean_folder(self) -> int:
        """Remove all files in the dbt path."""
        path = str((self.dbt_path / "*.sql").resolve())
        files = glob.glob(path)
        for file in files:
            os.remove(file)
        return len(files)

    @classmethod
    def _generate_topic(cls, topic: IOTopic) -> str:
        """Generate the SQL for a given topic."""
        with_mqtt = cls._with_mqtt(topic.topic)
        fields = "".join([cls._generate_field(io_val) for io_val in topic.fields])
        return f"{{{{ config(materialized='table_with_connector') }}}}\nCREATE TABLE {{{{ this }}}} (\n{fields})\n{with_mqtt}\n"

    @staticmethod
    def _generate_field(io_value: IOValue):
        """Generate the SQL for a given field."""
        return f"\t{io_value.name}\t{io_value.data_type},\n"

    @staticmethod
    def _with_mqtt(topic: str):
        """Generate the SQL for the MQTT connector."""
        return f"{{{{ mqtt_with('{topic}') }}}}"
