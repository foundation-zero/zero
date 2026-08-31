import json
from pathlib import Path

import polars as pl

from ..atpx_meta import RawField, classify_fields
from ..base import ReaderBase
from ..types import IOResult


class AtpxReader(ReaderBase):
    """Reads the ATPX (A+T) field io list into an id -> key mapping.

    ATPX topics carry a single raw value each rather than fixed groupings of
    fields, so no topics are emitted. The vector generator consumes the mapping
    to resolve each message's field name (senders it reads directly; see
    vector_gen/atpx.py).
    """

    def read_io_list(self, paths: list[Path]) -> IOResult:
        # Each file carries a `fields` list; later files extend the set.
        raw_fields: list[RawField] = []
        for path in paths:
            entries = json.loads(path.read_text()).get("fields", [])
            raw_fields.extend(RawField.model_validate(entry) for entry in entries)
        fields = classify_fields(raw_fields)

        io_list = pl.DataFrame(
            {
                "id": [f.id for f in fields],
                "key": [f.key for f in fields],
            }
        )

        return IOResult(io_list=io_list, topics=[])
