"""The history-migration spec: which old topic's rows go to which new topic, column by column.

`build_spec` makes it from a committed mapping of MQTT topics and keys, by running the real
Vector on every old and new topic and key. Vector decides the table and column names, so the
spec never depends on a reimplementation of its naming rules.
"""

import csv
import json
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from zero_data.greptime.config import PROJECT_ROOT

VECTOR_DIR = PROJECT_ROOT.parent / "vector"
VECTOR_IMAGE = "timberio/vector:0.55.0-debian"
MAPPING_FIELDS = ("old_topic", "old_key", "new_topic", "new_key")

VectorEvent = dict[str, object]
VectorRunner = Callable[[list[dict[str, str]]], list[VectorEvent]]


class SpecRefused(Exception):
    pass


class ColumnMap(BaseModel):
    model_config = ConfigDict(frozen=True)

    old: str
    new: str


class Unit(BaseModel):
    """One old topic in one old table, copied to one new topic in one new table."""

    model_config = ConfigDict(frozen=True)

    old_table: str
    old_topic: str
    new_table: str
    new_topic: str
    technical_name: str
    columns: list[ColumnMap]

    @property
    def label(self) -> str:
        return f"{self.old_topic} -> {self.new_topic}"


class MigrationSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    units: list[Unit]

    @property
    def old_tables(self) -> list[str]:
        return sorted({unit.old_table for unit in self.units})


def read_spec(path: Path) -> MigrationSpec:
    return MigrationSpec.model_validate_json(path.read_bytes())


class MappingRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    old_topic: str
    old_key: str
    new_topic: str
    new_key: str


def read_mapping(path: Path) -> list[MappingRow]:
    with path.open(newline="") as mapping_file:
        reader = csv.DictReader(mapping_file)
        if tuple(reader.fieldnames or ()) != MAPPING_FIELDS:
            raise SpecRefused(f"{path} must have the columns {MAPPING_FIELDS}")
        return [MappingRow.model_validate(row) for row in reader]


def _vector_case(case: str, topic: str, key: str) -> dict[str, str]:
    reading = {
        "Value": 1.5,
        "TimeStamp": "2026-06-01T12:00:00Z",
        "IsValid": True,
        "HasValue": True,
    }
    return {
        "timestamp": "2026-06-01T12:00:00Z",
        "topic": topic,
        "message": json.dumps({key: reading, "ZzCase": case}),
    }


def run_vector(cases: list[dict[str, str]]) -> list[VectorEvent]:
    """What the repo's Vector processing makes of each message, through Docker."""
    with tempfile.TemporaryDirectory(dir=VECTOR_DIR / "tests") as scratch:
        work = Path(scratch)
        (work / "cases.jsonl").write_text(
            "".join(json.dumps(case) + "\n" for case in cases)
        )
        config = (VECTOR_DIR / "tests/process-config.yaml").read_text()
        (work / "config.yaml").write_text(
            config.replace(
                "tests/process-test-cases.jsonl", f"tests/{work.name}/cases.jsonl"
            )
        )
        command = [
            "docker",
            "run",
            "--rm",
            "-w",
            "/home/vector",
            "-v",
            f"{VECTOR_DIR}:/home/vector",
            VECTOR_IMAGE,
            "--config",
            f"tests/{work.name}/config.yaml",
            "-q",
            "-q",
        ]
        output = subprocess.run(command, capture_output=True, text=True, check=True)
    return [
        json.loads(line) for line in output.stdout.splitlines() if line.startswith("{")
    ]


def _column(event: VectorEvent) -> str:
    (column,) = [
        name.removesuffix("__value") for name in event if name.endswith("__value")
    ]
    return column


def build_spec(
    mapping: list[MappingRow], vector: VectorRunner = run_vector
) -> MigrationSpec:
    cases = [
        _vector_case(f"{side}{index}", topic, key)
        for index, row in enumerate(mapping)
        for side, topic, key in (
            ("old", row.old_topic, row.old_key),
            ("new", row.new_topic, row.new_key),
        )
    ]
    events = {
        str(event["zz_case"]): event for event in vector(cases) if "zz_case" in event
    }
    dropped = sorted(
        f"{case['topic']} {case['message']}"
        for case in cases
        if json.loads(case["message"])["ZzCase"] not in events
    )
    if dropped:
        raise SpecRefused(f"Vector dropped {len(dropped)} messages: {dropped[:5]}")

    columns: dict[tuple[str, str], dict[str, str]] = {}
    tables: dict[tuple[str, str], tuple[str, str, str]] = {}
    for index, row in enumerate(mapping):
        old, new = events[f"old{index}"], events[f"new{index}"]
        key = (row.old_topic, row.new_topic)
        if "technical_name" not in new:
            raise SpecRefused(f"Vector gives {row.new_topic} no technical_name")
        tables[key] = (
            str(old["table"]),
            str(new["table"]),
            str(new["technical_name"]),
        )
        mapped = columns.setdefault(key, {})
        if mapped.setdefault(_column(old), _column(new)) != _column(new):
            raise SpecRefused(
                f"{row.old_topic} {row.old_key} maps to two columns of {row.new_topic}"
            )

    old_tables = {old_table for old_table, _, _ in tables.values()}
    overwritten = sorted(
        {new_table for _, new_table, _ in tables.values()} & old_tables
    )
    if overwritten:
        raise SpecRefused(f"New tables that are also old tables: {overwritten}")
    return MigrationSpec(
        units=[
            Unit(
                old_table=tables[key][0],
                old_topic=key[0],
                new_table=tables[key][1],
                new_topic=key[1],
                technical_name=tables[key][2],
                columns=[
                    ColumnMap(old=old, new=new)
                    for old, new in sorted(columns[key].items())
                ],
            )
            for key in sorted(columns)
        ]
    )
