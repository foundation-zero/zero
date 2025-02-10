import os
import glob
from pathlib import Path
from typing import List

from io_processing.io_list import IOTopic, IOValue


class MarpowerRawGenerator:
    def __init__(self, dbt_path: Path, io_topics: List[IOTopic]):
        self.io_topics = io_topics
        self.dbt_path = dbt_path / "models/raw/marpower/"

    def generate(self):
        number_of_files_removed = self._clean_folder()
        for topic in self.io_topics:
            file_name = topic.topic.lower()
            file_path = (self.dbt_path / f"{file_name}.sql").resolve()
            table = self._generate_topic(topic)
            with open(file_path, "w") as f:
                f.write(table)
        number_of_new_files = len(self.io_topics)
        print(f"Written marpower raw tables to {self.dbt_path.resolve()}")
        print(f"""    Created: {number_of_new_files} 
    Removed: {number_of_files_removed} 
    Delta: {number_of_new_files - number_of_files_removed}""")

    def _generate_topic(self, topic: IOTopic) -> str:
        with_mqtt = self.with_mqtt(topic.topic)
        fields = "".join([self._generate_field(io_val) for io_val in topic.fields])
        return f"{{{{ config(materialized='table_with_connector') }}}}\nCREATE TABLE {{{{ this }}}} (\n{fields})\n{with_mqtt}"

    def _clean_folder(self) -> int:
        path = str((self.dbt_path / "*.sql").resolve())
        files = glob.glob(path)
        for file in files:
            os.remove(file)
        return len(files)

    @staticmethod
    def _generate_field(io_value: IOValue):
        return f"\t{io_value.name}\t{io_value.data_type},\n"

    @staticmethod
    def with_mqtt(topic: str):
        return f"{{{{ mqtt_with('{topic}') }}}}"
