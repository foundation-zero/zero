"""Turns raw ATPX (A+T) field/sender descriptions into the slugs Vector stores.

Field slugs are not deduplicated: a few field_ids share a description (bit-12 id
pairs, e.g. 514/4610 "Boat Speed (kts)") and thus a slug; the raw MQTT topic
carries field_id and keeps those rows apart (ZERO-1660).
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel


class RawField(BaseModel):
    """One entry from the `fields` list of atpx_fields.json / atpx_extra.json."""

    id: int
    description: str


class RawSender(BaseModel):
    """One entry from atpx_senders.json (or atpx_extra.json's `senders` list)."""

    id: int
    source: str


@dataclass(frozen=True)
class AtpxField:
    id: int
    key: str


def slugify(text: str) -> str:
    """Turn a field/sender description into a snake_case identifier."""
    text = text.replace("&deg;", "deg").replace("->", "_to_")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def classify_fields(raw_fields: list[RawField]) -> list[AtpxField]:
    """Map each raw atpx field entry to its id and slugified name."""
    return [
        AtpxField(id=raw.id, key=slugify(raw.description))
        for raw in sorted(raw_fields, key=lambda f: f.id)
    ]


def read_senders(path: Path) -> dict[int, str]:
    """Read a sender id -> name map from an atpx senders file.

    Accepts both a bare list (atpx_senders.json) and a dict nesting them under
    a `senders` key (atpx_extra.json).
    """
    raw = json.loads(path.read_text())
    entries = raw["senders"] if isinstance(raw, dict) else raw
    senders = [RawSender.model_validate(entry) for entry in entries]
    return {sender.id: sender.source for sender in senders}
