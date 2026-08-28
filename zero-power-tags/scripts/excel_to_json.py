#!/usr/bin/env python3
"""Parse power-tag Excel files into modbus_bridges.json.

Each .xlsm = one panel workbook.
Each sheet lists breakers (CODE + CONSUMER columns).
Breakers are emitted as `(panel, name)` pairs plus their static attributes;
the full `power-tags/{panel}/{name}` topic, the register layout and the
engineering units are all documented by the `PowerTag` pydantic model at
runtime, so they are not duplicated here.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import polars as pl

SCRIPTS_FOLDER = Path(__file__).parent
DOCS_FOLDER = SCRIPTS_FOLDER / "../docs"


def slugify(text: str, code: str) -> str:
    """Turn a consumer name into a URL-friendly slug. Falls back to code."""
    s = text.lower()
    s = re.sub(r"[^a-z0-9\s-]+", "", s)
    s = re.sub(r"\s+", "-", s)
    s = s.strip("-")
    if not s:
        s = code.lower()
    # Collapse multiple dashes
    s = re.sub(r"-{2,}", "-", s)
    if len(s) > 60:
        s = s[:60].rstrip("-")
    return s


def load_patches(patches_path: Path | None) -> dict[str, dict[str, object]]:
    if patches_path is None or not patches_path.exists():
        return {}
    with open(patches_path, "r", encoding="utf-8") as f:
        return json.loads(f.read())


def _parse_args() -> tuple[Path | None, list[Path]]:
    """Parse CLI args: optional --patches <path>, then Excel file paths."""
    patches_path = None
    args = sys.argv[1:]
    if args and args[0] == "--patches":
        patches_path = Path(args[1])
        args = args[2:]

    if args:
        excel_files = [Path(a) for a in args]
    else:
        # Skip Office lock files (e.g. ~$book.xlsm) left by an open workbook.
        excel_files = sorted(
            p for p in DOCS_FOLDER.glob("*.xlsm") if not p.name.startswith("~$")
        )

    if not excel_files:
        print("No Excel files found in docs/", file=sys.stderr)
        sys.exit(1)

    return patches_path, excel_files


def _read_breakers(
    df: pl.DataFrame, panel: str, patches: dict
) -> list[tuple[str, str, str]]:
    """Extract raw breaker rows from a DataFrame, applying consumer patches."""
    cols = df.columns
    code_col = cols[1]
    consumer_col = cols[2]

    def parse_row(index: int) -> tuple[str, str, str] | None:
        code = df[code_col][index]
        if not code or str(code).strip() == "CODE":
            return None
        code = str(code).strip()
        consumer = str(df[consumer_col][index]).strip() if df[consumer_col][index] else ""
        patched = patches.get(f"{panel}/{code}", {}).get("_consumer") or patches.get(
            code, {}
        ).get("_consumer")
        if patched:
            consumer = patched
        return code, consumer, slugify(consumer, code)

    return [
        row for index in range(3, df.height) if (row := parse_row(index)) is not None
    ]


def _deduplicate_slugs(
    raw: list[tuple[str, str, str]],
) -> list[tuple[str, str, str]]:
    """Append code suffix to duplicate slugs."""
    slug_counts: defaultdict[str, int] = defaultdict(int)
    for _, _, slug in raw:
        slug_counts[slug] += 1

    return [
        (
            f"{slug}-{code.lower()}" if slug_counts[slug] > 1 else slug,
            code,
            consumer,
        )
        for code, consumer, slug in raw
    ]


def _breaker_unit_id(panel: str, code: str, fallback: int, patches: dict) -> int:
    """Slave id for one breaker: `_unit_id` patch when pinned, else sequential."""
    patched = patches.get(f"{panel}/{code}", {}).get("_unit_id") or patches.get(
        code, {}
    ).get("_unit_id")
    return int(patched) if patched else fallback


def _build_panel_topics(
    final: list[tuple[str, str, str]],
    panel: str,
    patches: dict,
) -> list[dict]:
    """Build breaker dicts for one panel's breakers.

    Each breaker is its own Modbus slave behind the gateway, so topics carry
    per-breaker slave ids (sequential unless pinned via a `_unit_id` patch);
    identical register layouts per breaker never alias.
    """
    topics = [
        {
            "unit_id": _breaker_unit_id(panel, code, index, patches),
            "name": slug,
            "extra_fields": [
                {"field_name": "component", "value": code},
                {"field_name": "panel", "value": panel},
                {"field_name": "consumer", "value": consumer},
            ],
        }
        for index, (slug, code, consumer) in enumerate(final, start=1)
    ]

    unit_ids = [t["unit_id"] for t in topics]
    duplicates = sorted({uid for uid in unit_ids if unit_ids.count(uid) > 1})
    if duplicates:
        raise ValueError(
            f"duplicate Modbus slave ids on panel {panel}: {duplicates} "
            "(sequential fallback collided with a pinned `_unit_id` patch; "
            "pin every conflicting breaker)"
        )
    return topics


def _process_excel_file(xlsx_path: Path, patches: dict) -> dict | None:
    """Process one Excel file into a unit dict, or None on failure."""
    sheets = pl.read_excel(xlsx_path, sheet_id=0)
    if not sheets:
        print(f"Warning: no sheets in {xlsx_path.name}", file=sys.stderr)
        return None

    panel = list(sheets.keys())[0]
    df = sheets[panel]

    raw = _read_breakers(df, panel, patches)
    final = _deduplicate_slugs(raw)
    topics = _build_panel_topics(final, panel, patches)

    print(f"{xlsx_path.name} → {panel}: {len(topics)} breakers")
    return {"panel": panel, "topics": topics}


def main() -> None:
    patches_path, excel_files = _parse_args()
    patches = load_patches(patches_path)

    units = [
        unit
        for xlsx_path in excel_files
        if (unit := _process_excel_file(xlsx_path, patches)) is not None
    ]

    output_path = SCRIPTS_FOLDER / "../modbus_bridges.json"
    output_path.write_text(json.dumps(units, indent=2, ensure_ascii=False))
    total = sum(len(u["topics"]) for u in units)
    print(
        f"Wrote {len(units)} ModbusUnit(s), {total} breaker(s) to {output_path.resolve()}"
    )


if __name__ == "__main__":
    main()
