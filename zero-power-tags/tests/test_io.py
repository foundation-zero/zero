import json
from pathlib import Path

import pytest
from zero_modbus_bridge.io import ModbusTopic, RegisterValue

from zero_power_tags.io import (
    BridgeSpec,
    PowerTag,
    build_asyncapi,
    modbus_host_env,
    modbus_port_env,
    parse_topic,
    read_modbus_bridge_specs,
    read_topics_metadata,
)


class TestParseTopic:
    """_parse_topic builds ModbusTopic from a bridge entry dict."""

    def test_extra_fields_as_list(self):
        raw: dict = {
            "name": "t1",
            "unit_id": 1,
            "extra_fields": [
                {"field_name": "panel", "value": "10P0.1"},
                {"field_name": "component", "value": "ABC"},
            ],
        }
        topic = parse_topic(raw, panel="test")
        assert isinstance(topic, ModbusTopic)
        assert topic.topic == "power-tags/test/t1"
        assert topic.unit_id == 1
        assert topic.fields[0].register == 3000
        assert topic.model is PowerTag
        assert topic.extra_fields == {"panel": "10P0.1", "component": "ABC"}

    def test_extra_fields_as_dict(self):
        raw: dict = {
            "name": "t2",
            "unit_id": 2,
            "extra_fields": {"panel": "10P0.2", "component": "DEF"},
        }
        topic = parse_topic(raw, panel="test")
        assert topic.extra_fields == {"panel": "10P0.2", "component": "DEF"}

    def test_extra_fields_empty_list(self):
        raw: dict = {
            "name": "t3",
            "unit_id": 3,
            "extra_fields": [],
        }
        topic = parse_topic(raw, panel="test")
        assert topic.extra_fields == {}

    def test_extra_fields_omitted(self):
        raw: dict = {
            "name": "t4",
            "unit_id": 4,
        }
        topic = parse_topic(raw, panel="test")
        assert topic.extra_fields == {}

    def test_annotation_model_has_valid_converter(self):
        raw: dict = {
            "name": "t5",
            "unit_id": 1,
        }
        topic = parse_topic(raw, panel="test")
        assert topic.converter is not None

    def test_extra_fields_survive_serialization(self):
        """component/panel/consumer are part of the payload (data collection)."""
        raw: dict = {
            "name": "t6",
            "unit_id": 1,
            "extra_fields": {
                "panel": "10P1",
                "component": "150F01",
                "consumer": "TEST CONSUMER",
            },
        }
        topic = parse_topic(raw, panel="test")
        # Converter maps values positionally over all annotated fields;
        # active_power_total is the 11th electrical field.
        registers: list[RegisterValue] = [
            (3000 + i * 2, 21.0 if i == 10 else None) for i in range(15)
        ]
        payload = topic.converter(registers)
        dumped = payload.model_dump()
        assert dumped["active_power_total"] == pytest.approx(21.0)
        assert dumped["component"] == "150F01"
        assert dumped["panel"] == "10P1"
        assert dumped["consumer"] == "TEST CONSUMER"


class TestModbusEnvNames:
    """Panel names map to sanitized env var suffixes."""

    def test_host_env_name(self):
        assert modbus_host_env("10P0.1") == "MODBUS_HOST_10P0_1"

    def test_port_env_name(self):
        assert modbus_port_env("10P0.3") == "MODBUS_PORT_10P0_3"

    def test_plain_panel_name_unchanged(self):
        assert modbus_host_env("10P1") == "MODBUS_HOST_10P1"

    def test_lowercased_and_dasherized_panel(self):
        assert modbus_host_env("ab-cd") == "MODBUS_HOST_AB_CD"


class TestReadModbusBridgeSpecs:
    """read_modbus_bridge_specs groups the bridges JSON per gateway."""

    def test_groups_per_entry(self, bridges_json: Path):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MODBUS_BRIDGES_PATH", str(bridges_json))
            specs = read_modbus_bridge_specs()
        assert [spec.panel for spec in specs] == ["10P0.1", "10P0.2"]
        assert [topic.unit_id for spec in specs for topic in spec.topics] == [1, 2]
        assert [spec.topics[0].topic for spec in specs] == [
            "power-tags/10P0.1/test-device",
            "power-tags/10P0.2/test-device",
        ]
        assert all(
            isinstance(topic, ModbusTopic) for spec in specs for topic in spec.topics
        )

    def test_env_var_overrides_default_path(self, tmp_path: Path):
        alt = tmp_path / "alt.json"
        alt.write_text(
            json.dumps(
                [
                    {
                        "panel": "test",
                        "topics": [
                            {
                                "unit_id": 5,
                                "name": "override",
                            }
                        ],
                    }
                ]
            )
        )
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MODBUS_BRIDGES_PATH", str(alt))
            specs = read_modbus_bridge_specs()
        assert len(specs) == 1
        assert specs[0].panel == "test"
        assert specs[0].topics[0].unit_id == 5
        assert specs[0].topics[0].topic == "power-tags/test/override"

    def test_file_not_found(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MODBUS_BRIDGES_PATH", "/nonexistent/bridges.json")
            with pytest.raises(FileNotFoundError):
                read_modbus_bridge_specs()

    def test_invalid_json(self, tmp_path: Path):
        bad = tmp_path / "bad.json"
        bad.write_text("not json")
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MODBUS_BRIDGES_PATH", str(bad))
            with pytest.raises(json.JSONDecodeError):
                read_modbus_bridge_specs()

    def test_default_path_reads_project_file(self):
        """Without env var, reads the real modbus_bridges.json in the project root."""
        with pytest.MonkeyPatch.context() as mp:
            mp.delenv("MODBUS_BRIDGES_PATH", raising=False)
            specs = read_modbus_bridge_specs()
        assert {spec.panel for spec in specs} == {
            "10P0.1",
            "10P0.3",
            "10P1",
            "10P2",
            "10P3",
        }
        assert all(isinstance(spec, BridgeSpec) and spec.topics for spec in specs)


class TestReadTopicsMetadata:
    """read_topics_metadata transforms bridges JSON into the metadata document."""

    def _write_bridges(self, tmp_path: Path, units: list[dict]) -> Path:
        path = tmp_path / "bridges.json"
        path.write_text(json.dumps(units), encoding="utf-8")
        return path

    def test_metadata_entry_fields(self, tmp_path: Path):
        bridges = self._write_bridges(
            tmp_path,
            [
                {
                    "panel": "10P1",
                    "topics": [
                        {
                            "name": "test-consumer",
                            "extra_fields": [
                                {"field_name": "component", "value": "150F01"},
                                {"field_name": "panel", "value": "10P1"},
                                {"field_name": "consumer", "value": "TEST CONSUMER"},
                            ],
                        }
                    ],
                }
            ],
        )
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MODBUS_BRIDGES_PATH", str(bridges))
            doc = read_topics_metadata()

        assert doc["group"] == "power-tags"
        assert doc["topics"] == [
            {
                "topic": "power-tags/10P1/test-consumer",
                "metadata": {
                    "panel": "10P1",
                    "slug": "test-consumer",
                    "component": "150F01",
                    "consumer": "TEST CONSUMER",
                },
            }
        ]

    def test_missing_attributes_are_none(self, tmp_path: Path):
        bridges = self._write_bridges(
            tmp_path,
            [
                {
                    "panel": "x",
                    "topics": [
                        {
                            "name": "y",
                            "extra_fields": {"component": "1F01"},
                        }
                    ],
                }
            ],
        )
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MODBUS_BRIDGES_PATH", str(bridges))
            entry = read_topics_metadata()["topics"][0]

        assert entry["metadata"]["component"] == "1F01"
        assert entry["metadata"]["consumer"] is None
        assert entry["metadata"]["panel"] == "x"
        assert entry["metadata"]["slug"] == "y"

    def test_project_metadata_is_complete(self):
        """The checked-in bridges file yields full metadata for every breaker."""
        with pytest.MonkeyPatch.context() as mp:
            mp.delenv("MODBUS_BRIDGES_PATH", raising=False)
            doc = read_topics_metadata()

        topics = doc["topics"]
        assert len(topics) > 0
        assert all(t["topic"].startswith("power-tags/") for t in topics)
        assert all(
            None not in t["metadata"].values()
            and set(t["metadata"]) == {"panel", "slug", "component", "consumer"}
            for t in topics
        )


class TestBuildAsyncapi:
    """build_asyncapi emits a FastStream parametrized channel with enums."""

    def _write_bridges(self, tmp_path: Path, units: list[dict]) -> Path:
        path = tmp_path / "bridges.json"
        path.write_text(json.dumps(units), encoding="utf-8")
        return path

    @staticmethod
    def _breaker(name: str, unit_id: int = 1) -> dict:
        return {
            "unit_id": unit_id,
            "name": name,
            "extra_fields": [],
        }

    def test_parametrized_channel(self, tmp_path: Path):
        bridges = self._write_bridges(
            tmp_path,
            [
                {
                    "panel": "10P1",
                    "topics": [self._breaker("pump-a"), self._breaker("pump-c")],
                },
                {
                    "panel": "10P2",
                    "topics": [self._breaker("pump-b", unit_id=1)],
                },
            ],
        )
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MODBUS_BRIDGES_PATH", str(bridges))
            doc = build_asyncapi()

        # FastStream keys the channel by (clear_key of) the publisher title,
        # which for a parametrized publisher is the template itself and also
        # serves as the channel address.
        channel = doc["channels"]["power-tags.{panel}.{slug}"]
        assert channel["address"] == "power-tags/{panel}/{slug}"
        assert channel["bindings"]["mqtt"]["topic"] == "power-tags/+/+"
        assert set(doc["channels"]) == {"power-tags.{panel}.{slug}"}
        assert channel["parameters"]["panel"]["enum"] == ["10P1", "10P2"]
        assert channel["parameters"]["slug"]["enum"] == ["pump-a", "pump-b", "pump-c"]

    def test_message_refs_survive_braced_channels(self, tmp_path: Path):
        """Braces stay raw in component keys; $ref pointers are decoded to match."""
        bridges = self._write_bridges(
            tmp_path,
            [
                {
                    "panel": "10P1",
                    "topics": [self._breaker("pump-a")],
                }
            ],
        )
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MODBUS_BRIDGES_PATH", str(bridges))
            doc = build_asyncapi()

        channel = doc["channels"]["power-tags.{panel}.{slug}"]
        message_ref = channel["messages"]["Message"]["$ref"]
        assert "%" not in message_ref
        assert message_ref.startswith("#/components/messages/power-tags.")
        assert list(doc["components"]["messages"]) == [message_ref.split("/")[-1]]

    def test_payload_schema_fields(self):
        schema = PowerTag.model_json_schema()
        assert set(schema["properties"]) == {
            "component",
            "panel",
            "consumer",
            "current_a",
            "current_b",
            "current_c",
            "current_n",
            "voltage_an",
            "voltage_bn",
            "voltage_cn",
            "active_power_a",
            "active_power_b",
            "active_power_c",
            "active_power_total",
            "power_factor_a",
            "power_factor_b",
            "power_factor_c",
            "power_factor_total",
        }

    def test_payload_schema_units(self):
        schema = PowerTag.model_json_schema()
        assert schema["properties"]["current_a"]["x-unit"] == "A"
        assert schema["properties"]["voltage_an"]["x-unit"] == "V"
        assert schema["properties"]["active_power_total"]["x-unit"] == "W"
        assert "x-unit" not in schema["properties"]["power_factor_total"]

    def test_project_document_channel(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.delenv("MODBUS_BRIDGES_PATH", raising=False)
            doc = build_asyncapi()

        # One parametrized channel covering every panel, with the option
        # space documented as parameter enums.
        channel = doc["channels"]["power-tags.{panel}.{slug}"]
        assert channel["address"] == "power-tags/{panel}/{slug}"
        assert channel["bindings"]["mqtt"]["topic"] == "power-tags/+/+"
        assert channel["parameters"]["panel"]["enum"] == [
            "10P0.1",
            "10P0.3",
            "10P1",
            "10P2",
            "10P3",
        ]
        assert 0 < len(channel["parameters"]["slug"]["enum"]) <= 226

    def test_project_document_schema_units(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.delenv("MODBUS_BRIDGES_PATH", raising=False)
            doc = build_asyncapi()

        schema = doc["components"]["schemas"]["PowerTag"]
        assert schema["properties"]["current_a"]["x-unit"] == "A"
        assert schema["properties"]["active_power_total"]["x-unit"] == "W"
