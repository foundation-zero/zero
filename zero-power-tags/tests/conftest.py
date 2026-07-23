import json
from pathlib import Path
from typing import Any

import pytest

SAMPLE_BRIDGES: list[dict[str, Any]] = [
    {
        "unit_id": 1,
        "topics": [
            {
                "topic": "power-tags/10P0.1/test-device",
                "modbus_fields": [
                    {
                        "modbus_register": 3000,
                        "field_name": "current_a",
                        "description": "RMS current phase A",
                        "scale_factor": 1.0,
                        "register_count": 2,
                        "data_type": "float32",
                        "modbus_type": "holding",
                        "invalid_value": 4290772992,
                        "unit": "A",
                    }
                ],
                "extra_fields": [
                    {"field_name": "component", "value": "TEST01"},
                    {"field_name": "panel", "value": "10P0.1"},
                ],
            }
        ],
    },
    {
        "unit_id": 2,
        "topics": [
            {
                "topic": "power-tags/10P0.2/test-device",
                "modbus_fields": [
                    {
                        "modbus_register": 4000,
                        "field_name": "current_a",
                        "description": "RMS current phase A",
                        "scale_factor": 1.0,
                        "register_count": 2,
                        "data_type": "float32",
                        "modbus_type": "holding",
                        "invalid_value": 4290772992,
                        "unit": "A",
                    }
                ],
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
