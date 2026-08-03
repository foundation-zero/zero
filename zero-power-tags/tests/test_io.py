import json
from pathlib import Path

import pytest
from zero_modbus_bridge.io import ModbusTopic

from zero_power_tags.io import PowerTag, parse_topic, read_modbus_topics


class TestParseTopic:
    """_parse_topic builds ModbusTopic from a bridge entry dict."""

    def test_extra_fields_as_list(self):
        raw: dict = {
            "topic": "power-tags/test/t1",
            "modbus_fields": [
                {
                    "modbus_register": 3000,
                    "field_name": "current_a",
                    "scale_factor": 1.0,
                    "register_count": 2,
                    "data_type": "float32",
                    "modbus_type": "holding",
                    "description": "",
                    "unit": "A",
                }
            ],
            "extra_fields": [
                {"field_name": "panel", "value": "10P0.1"},
                {"field_name": "component", "value": "ABC"},
            ],
        }
        topic = parse_topic(raw, unit_id=1)
        assert isinstance(topic, ModbusTopic)
        assert topic.topic == "power-tags/test/t1"
        assert topic.unit_id == 1
        assert topic.start_register == 3000
        assert topic.model is PowerTag
        assert topic.extra_fields == {"panel": "10P0.1", "component": "ABC"}

    def test_extra_fields_as_dict(self):
        raw: dict = {
            "topic": "power-tags/test/t2",
            "modbus_fields": [
                {
                    "modbus_register": 4000,
                    "field_name": "current_a",
                    "scale_factor": 1.0,
                    "register_count": 2,
                    "data_type": "float32",
                    "modbus_type": "holding",
                    "description": "",
                    "unit": "A",
                }
            ],
            "extra_fields": {"panel": "10P0.2", "component": "DEF"},
        }
        topic = parse_topic(raw, unit_id=2)
        assert topic.extra_fields == {"panel": "10P0.2", "component": "DEF"}

    def test_extra_fields_empty_list(self):
        raw: dict = {
            "topic": "power-tags/test/t3",
            "modbus_fields": [
                {
                    "modbus_register": 5000,
                    "field_name": "current_a",
                    "scale_factor": 1.0,
                    "register_count": 2,
                    "data_type": "float32",
                    "modbus_type": "holding",
                    "description": "",
                    "unit": "A",
                }
            ],
            "extra_fields": [],
        }
        topic = parse_topic(raw, unit_id=3)
        assert topic.extra_fields == {}

    def test_extra_fields_omitted(self):
        raw: dict = {
            "topic": "power-tags/test/t4",
            "modbus_fields": [
                {
                    "modbus_register": 6000,
                    "field_name": "current_a",
                    "scale_factor": 1.0,
                    "register_count": 2,
                    "data_type": "float32",
                    "modbus_type": "holding",
                    "description": "",
                    "unit": "A",
                }
            ],
        }
        topic = parse_topic(raw, unit_id=4)
        assert topic.extra_fields == {}

    def test_annotation_model_has_valid_converter(self):
        raw: dict = {
            "topic": "power-tags/test/t5",
            "modbus_fields": [
                {
                    "modbus_register": 3000,
                    "field_name": "current_a",
                    "scale_factor": 1.0,
                    "register_count": 2,
                    "data_type": "float32",
                    "modbus_type": "holding",
                    "description": "",
                    "unit": "A",
                }
            ],
        }
        topic = parse_topic(raw, unit_id=1)
        assert topic.converter is not None


class TestReadModbusTopics:
    """read_modbus_topics loads and parses the full bridges JSON."""

    def test_default_path(self, bridges_json: Path):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MODBUS_BRIDGES_PATH", str(bridges_json))
            topics = read_modbus_topics()
        assert len(topics) == 2
        assert topics[0].topic == "power-tags/10P0.1/test-device"
        assert topics[0].unit_id == 1
        assert topics[0].start_register == 3000
        assert topics[1].topic == "power-tags/10P0.2/test-device"
        assert topics[1].unit_id == 2
        assert topics[1].start_register == 4000

    def test_env_var_overrides_default(self, bridges_json: Path, tmp_path: Path):
        alt = tmp_path / "alt.json"
        alt.write_text(
            json.dumps(
                [
                    {
                        "unit_id": 5,
                        "topics": [
                            {
                                "topic": "power-tags/test/override",
                                "modbus_fields": [
                                    {
                                        "modbus_register": 100,
                                        "field_name": "current_a",
                                        "scale_factor": 1.0,
                                        "register_count": 2,
                                        "data_type": "float32",
                                        "modbus_type": "holding",
                                        "description": "",
                                        "unit": "A",
                                    }
                                ],
                            }
                        ],
                    }
                ]
            )
        )
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MODBUS_BRIDGES_PATH", str(alt))
            topics = read_modbus_topics()
        assert len(topics) == 1
        assert topics[0].unit_id == 5

    def test_file_not_found(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MODBUS_BRIDGES_PATH", "/nonexistent/bridges.json")
            with pytest.raises(FileNotFoundError):
                read_modbus_topics()

    def test_invalid_json(self, tmp_path: Path):
        bad = tmp_path / "bad.json"
        bad.write_text("not json")
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MODBUS_BRIDGES_PATH", str(bad))
            with pytest.raises(json.JSONDecodeError):
                read_modbus_topics()

    def test_default_path_reads_project_file(self):
        """Without env var, reads the real modbus_bridges.json in the project root."""
        with pytest.MonkeyPatch.context() as mp:
            mp.delenv("MODBUS_BRIDGES_PATH", raising=False)
            topics = read_modbus_topics()
        assert len(topics) > 0
        assert all(isinstance(t, ModbusTopic) for t in topics)
