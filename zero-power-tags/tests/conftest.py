import json
from pathlib import Path
from typing import Any

import pytest

SAMPLE_BRIDGES: list[dict[str, Any]] = [
    {
        "panel": "10P0.1",
        "topics": [
            {
                "unit_id": 1,
                "name": "test-device",
                "extra_fields": [
                    {"field_name": "component", "value": "TEST01"},
                    {"field_name": "panel", "value": "10P0.1"},
                ],
            }
        ],
    },
    {
        "panel": "10P0.2",
        "topics": [
            {
                "unit_id": 2,
                "name": "test-device",
                "extra_fields": {"component": "TEST02", "panel": "10P0.2"},
            }
        ],
    },
]


@pytest.fixture
def bridges_json(tmp_path: Path) -> Path:
    """Write SAMPLE_BRIDGES to a temp JSON file and return the path."""
    path = tmp_path / "modbus_bridges.json"
    path.write_text(json.dumps(SAMPLE_BRIDGES), encoding="utf-8")
    return path
