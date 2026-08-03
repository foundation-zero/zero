#!/usr/bin/env python3
"""Parse power-tag Excel files into modbus_bridges.json.

Each .xlsm = one panel workbook.
Each sheet lists breakers (CODE + CONSUMER columns).
MQTT topic: power-tags/{panel}/{consumer-slug} with code suffix on collisions.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import polars as pl

SCRIPTS_FOLDER = Path(__file__).parent
DOCS_FOLDER = SCRIPTS_FOLDER / "../docs"

REGISTERS: list[tuple[int, str, str, str]] = [
    (3000, "current_a", "A", "RMS current phase A"),
    (3002, "current_b", "A", "RMS current phase B"),
    (3004, "current_c", "A", "RMS current phase C"),
    (3006, "current_n", "A", "RMS current Neutral"),
    (3028, "voltage_an", "V", "RMS voltage A-N"),
    (3030, "voltage_bn", "V", "RMS voltage B-N"),
    (3032, "voltage_cn", "V", "RMS voltage C-N"),
    (3054, "active_power_a", "W", "Active power phase A"),
    (3056, "active_power_b", "W", "Active power phase B"),
    (3058, "active_power_c", "W", "Active power phase C"),
    (3060, "active_power_total", "W", "Total active power"),
    (3078, "power_factor_a", "", "Power factor phase A"),
    (3080, "power_factor_b", "", "Power factor phase B"),
    (3082, "power_factor_c", "", "Power factor phase C"),
    (3084, "power_factor_total", "", "Total power factor"),
]

# NaN sentinel decoded from float32 0xFFC00000 is rejected at read time by
# each field's ``is_finite_float`` validator (see zero_modbus_bridge.bit_ops)


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


def build_address_dicts() -> list[dict]:
    return [
        {
            "modbus_register": reg,
            "field_name": name,
            "description": desc,
            "register_count": 2,
            "data_type": "float32",
            "modbus_type": "holding",
        }
        for reg, name, unit, desc in REGISTERS
    ]

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
        excel_files = sorted(DOCS_FOLDER.glob("*.xlsm"))

    if not excel_files:
        print("No Excel files found in docs/", file=sys.stderr)
        sys.exit(1)

    return patches_path, excel_files


def _read_breakers(
    df: pl.DataFrame, panel: str, patches: dict
) -> list[tuple[str, str, str, str]]:
    """Extract raw breaker rows from a DataFrame, applying consumer patches."""
    cols = df.columns
    code_col = cols[1]
    consumer_col = cols[2]

    raw: list[tuple[str, str, str, str]] = []
    for i in range(3, df.height):
        code = df[code_col][i]
        if not code or str(code).strip() == "CODE":
            continue
        code = str(code).strip()
        consumer = str(df[consumer_col][i]).strip() if df[consumer_col][i] else ""
        patch_key = f"{panel}/{code}"
        patched = patches.get(patch_key, {}).get("_consumer") or patches.get(code, {}).get("_consumer")
        if patched:
            consumer = patched
        slug = slugify(consumer, code)
        raw.append((code, consumer, slug, consumer))
    return raw


def _deduplicate_slugs(
    raw: list[tuple[str, str, str, str]],
) -> list[tuple[str, str, str]]:
    """Append code suffix to duplicate slugs."""
    slug_counts: defaultdict[str, int] = defaultdict(int)
    for _, _, slug, _ in raw:
        slug_counts[slug] += 1

    final: list[tuple[str, str, str]] = []
    for code, consumer, slug, desc in raw:
        unique_slug = f"{slug}-{code.lower()}" if slug_counts[slug] > 1 else slug
        final.append((unique_slug, code, desc))
    return final


def _apply_breaker_patches(
    base_fields: list[dict], code: str, patches: dict
) -> list[dict]:
    """Apply per-breaker patches (scale_factor overrides) to base fields."""
    breaker_patches = patches.get(code, {})
    fields = [dict(f) for f in base_fields]
    for f in fields:
        if f["field_name"] in breaker_patches:
            override = breaker_patches[f["field_name"]]
            if isinstance(override, dict):
                f.update(override)
            else:
                f["scale_factor"] = float(override)
    return fields


def _build_panel_topics(
    final: list[tuple[str, str, str]],
    panel: str,
    patches: dict,
    base_fields: list[dict],
) -> list[dict]:
    """Build topic dicts for one panel's breakers."""
    topics: list[dict] = []
    for slug, code, desc in final:
        fields = _apply_breaker_patches(base_fields, code, patches)
        topics.append({
            "topic": f"power-tags/{panel}/{slug}",
            "modbus_fields": fields,
            "extra_fields": [
                {"field_name": "component", "value": code},
                {"field_name": "panel", "value": panel},
            ],
        })
    return topics


def _process_excel_file(
    xlsx_path: Path, patches: dict, base_fields: list[dict]
) -> dict | None:
    """Process one Excel file into a unit dict, or None on failure."""
    sheets = pl.read_excel(xlsx_path, sheet_id=0)
    if not sheets:
        print(f"Warning: no sheets in {xlsx_path.name}", file=sys.stderr)
        return None

    panel = list(sheets.keys())[0]
    df = sheets[panel]

    raw = _read_breakers(df, panel, patches)
    final = _deduplicate_slugs(raw)
    topics = _build_panel_topics(final, panel, patches, base_fields)

    print(f"{xlsx_path.name} → {panel}: {len(topics)} breakers")
    return {"unit_id": 1, "topics": topics}


def main() -> None:
    patches_path, excel_files = _parse_args()
    patches = load_patches(patches_path)
    base_fields = build_address_dicts()

    units: list[dict] = []
    for xlsx_path in excel_files:
        unit = _process_excel_file(xlsx_path, patches, base_fields)
        if unit:
            units.append(unit)

    output_path = SCRIPTS_FOLDER / "../modbus_bridges.json"
    output_path.write_text(json.dumps(units, indent=2, ensure_ascii=False))
    total = sum(len(u["topics"]) for u in units)
    print(f"Wrote {len(units)} ModbusUnit(s), {total} breaker(s) to {output_path.resolve()}")


if __name__ == "__main__":
    main()
