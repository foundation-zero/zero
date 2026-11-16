"""The history-migration spec: which old topic's rows go to which new topic, column by column.

Built outside zero-data (from the IO-list mapping and the real Vector rule); this module only
reads it. Fields the command doesn't use (row counts, provenance) are ignored.
"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict

SUFFIXES = ("value", "timestamp", "is_valid", "has_value")


class ColumnMap(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    old: str
    new: str
    suffixes: list[str]


class Unit(BaseModel):
    """One old topic in one old table, copied to one new topic in one new table."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    wave: int
    old_table: str
    old_topic: str
    new_table: str
    new_topic: str
    technical_name: str
    columns: list[ColumnMap]
    chain: str | None = None


class MigrationSpec(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    units: list[Unit]

    @property
    def old_tables(self) -> set[str]:
        return {unit.old_table for unit in self.units}


def read_spec(path: Path) -> MigrationSpec:
    return MigrationSpec.model_validate_json(path.read_bytes())
