from io_processing.io_list import IOValue
from typing import List
from pathlib import Path


class AMCSFieldMapCTEGenerator:
    def __init__(self, io_values: List[IOValue], dbt_path: Path):
        self.io_values = io_values
        self.file_path = (dbt_path / "models/raw/amcs_cte.sql").resolve()

    def generate(self):
        case_lines = list(map(lambda row: self._case_line(row),  self.io_values))
        macro = self._macro(case_lines)
        with open(self.file_path, "w") as f:
            f.write(macro)
        print(f"Wrote {len(case_lines)} cases to {self.file_path}")
        return macro

    def _case_line(self, io_value: IOValue):
        data_type = io_value.data_type
        topic = io_value.topic
        return f"""    CASE WHEN topic='{topic}' THEN CAST(convert_from(amcs.data,'utf-8') AS {data_type}) ELSE NULL END {topic}
"""

    def _macro(self, case_lines: List[str]):
        cases = "".join(case_lines)
        return f"""{{{{ config(materialized='ephemeral') }}}}
SELECT (
    timestamp,
{cases}
from amcs_input
"""
