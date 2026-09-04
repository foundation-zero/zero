"""Tests for the AsyncAPI 3.0.0 spec builder and the self-validating corpus."""

import json
from pathlib import Path
from typing import Any

import pytest

from zero_atpx_nmea.asyncapi_spec import build_spec
from zero_atpx_nmea.corpus import documented_types, sender_for, sentence_for
from zero_atpx_nmea.parser import parse


@pytest.fixture(scope="module")
def spec() -> dict[str, Any]:
    """The built spec, shared across tests (build_spec is pure and tests only read it)."""
    return build_spec()


def _parse_example(nmea_type: str) -> dict[str, Any] | None:
    """Run a documented type's corpus example through the real parser."""
    topic = f"atpx/nmea0183/{sender_for(nmea_type)}/{nmea_type.upper()}"
    return parse(sentence_for(nmea_type), topic)


def test_every_example_parses_successfully() -> None:
    """Every example sentence in the curated corpus must parse without error."""
    for nmea_type in documented_types():
        assert _parse_example(nmea_type) is not None, (
            f"Example for {nmea_type} failed to parse"
        )


def test_every_parsed_type_matches_corpus_type() -> None:
    """Each example's parsed ``type`` must match the type it's filed under."""
    for nmea_type in documented_types():
        envelope = _parse_example(nmea_type)
        assert envelope is not None
        assert envelope["type"] == nmea_type, (
            f"Expected type={nmea_type}, got {envelope['type']}"
        )


def test_documented_keys_match_parsed_keys(spec: dict[str, Any]) -> None:
    """The documented keys for each type must match what ``parse()`` actually emits.

    This guarantees the spec never describes fields the parser doesn't produce,
    or vice-versa.
    """
    for nmea_type in documented_types():
        envelope = _parse_example(nmea_type)
        assert envelope is not None

        msg = spec["components"]["messages"][f"{nmea_type}_envelope"]
        spec_props = set(msg["payload"]["properties"].keys())

        parsed_keys = set(envelope.keys())
        assert spec_props == parsed_keys, (
            f"Mismatch for {nmea_type}: spec has {spec_props - parsed_keys} "
            f"not in parse output, parse has {parsed_keys - spec_props} not in spec"
        )


class TestSpecTopLevel:
    """Top-level AsyncAPI document shape."""

    def test_asyncapi_version(self, spec: dict[str, Any]) -> None:
        assert spec["asyncapi"] == "3.0.0"

    def test_info_title(self, spec: dict[str, Any]) -> None:
        assert spec["info"]["title"] == "Zero ATPX NMEA"

    def test_info_version_is_string(self, spec: dict[str, Any]) -> None:
        version = spec["info"]["version"]
        assert isinstance(version, str) and len(version) > 0

    def test_info_description_mentions_broker_roles(self, spec: dict[str, Any]) -> None:
        desc = spec["info"]["description"]
        assert "A+T's onboard broker" in desc
        assert "our own MQTT broker" in desc

    def test_info_description_mentions_known_type_scope(
        self, spec: dict[str, Any]
    ) -> None:
        desc = spec["info"]["description"]
        assert "known/supported subset" in desc


class TestInputChannel:
    """The single input channel."""

    def test_input_channel_exists(self, spec: dict[str, Any]) -> None:
        channel_id = "atpx/nmea0183/{sender}/{TYPE}"
        assert channel_id in spec["channels"]

    def test_input_channel_has_string_payload(self, spec: dict[str, Any]) -> None:
        msg = spec["components"]["messages"]["raw_nmea_sentence"]
        assert msg["payload"]["type"] == "string"
        assert msg["contentType"] == "text/plain"

    def test_input_channel_has_sender_and_type_parameters(
        self, spec: dict[str, Any]
    ) -> None:
        channel_id = "atpx/nmea0183/{sender}/{TYPE}"
        ch = spec["channels"][channel_id]
        assert "sender" in ch["parameters"]
        assert "TYPE" in ch["parameters"]

    def test_input_operation_is_receive(self, spec: dict[str, Any]) -> None:
        op = spec["operations"]["receive_raw_nmea"]
        assert op["action"] == "receive"


class TestOutputChannels:
    """One output channel per documented type."""

    def test_one_channel_per_documented_type(self, spec: dict[str, Any]) -> None:
        types = documented_types()
        # +1 for the input channel
        assert len(spec["channels"]) == len(types) + 1

    def test_every_output_channel_has_correct_address(
        self, spec: dict[str, Any]
    ) -> None:
        for nmea_type in documented_types():
            channel_id = f"atpx/processed/nmea/{nmea_type}/{{sender}}"
            assert channel_id in spec["channels"]
            expected_address = f"atpx/processed/nmea/{nmea_type}/{{sender}}"
            assert spec["channels"][channel_id]["address"] == expected_address

    def test_every_output_has_send_operation(self, spec: dict[str, Any]) -> None:
        for nmea_type in documented_types():
            op_id = f"send_{nmea_type}_envelope"
            assert op_id in spec["operations"]
            assert spec["operations"][op_id]["action"] == "send"


class TestPerTypeSchemas:
    """Per-type message schema properties."""

    def test_always_present_envelope_keys(self, spec: dict[str, Any]) -> None:
        """Every per-type message must advertise ``type``/``sender``/``talker``/``raw``."""
        for nmea_type in documented_types():
            msg = spec["components"]["messages"][f"{nmea_type}_envelope"]
            props = msg["payload"]["properties"]
            for key in ("type", "sender", "talker", "raw"):
                assert key in props, f"{nmea_type} missing required key {key}"
                assert props[key]["type"] == ["string", "null"]

    def test_position_types_have_latitude_longitude(self, spec: dict[str, Any]) -> None:
        """GGA, GLL, and RMC must advertise ``latitude``/``longitude``."""
        for nmea_type in ("gga", "gll", "rmc"):
            msg = spec["components"]["messages"][f"{nmea_type}_envelope"]
            props = msg["payload"]["properties"]
            assert "latitude" in props, f"{nmea_type} missing latitude"
            assert "longitude" in props, f"{nmea_type} missing longitude"
            assert props["latitude"]["type"] == ["number", "null"]
            assert props["longitude"]["type"] == ["number", "null"]

    def test_position_types_have_nmea_time_not_timestamp(
        self, spec: dict[str, Any]
    ) -> None:
        """Position types must use the renamed ``nmea_time`` key, never ``timestamp``."""
        for nmea_type in ("gga", "gll", "rmc", "zda", "alr"):
            msg = spec["components"]["messages"][f"{nmea_type}_envelope"]
            props = msg["payload"]["properties"]
            assert "nmea_time" in props, f"{nmea_type} missing nmea_time"
            assert "timestamp" not in props, (
                f"{nmea_type} still has raw 'timestamp' key (should be nmea_time)"
            )

    def test_proprietary_type_has_manufacturer_and_data(
        self, spec: dict[str, Any]
    ) -> None:
        """The proprietary FEC type must advertise ``manufacturer`` and ``data``."""
        msg = spec["components"]["messages"]["fec_envelope"]
        props = msg["payload"]["properties"]
        assert "manufacturer" in props
        assert props["manufacturer"]["type"] == ["string", "null"]
        assert "data" in props
        assert props["data"]["type"] == ["array", "null"]


class TestFieldTypes:
    """Spot-check that numeric fields have correct JSON types."""

    def _assert_type(self, props: dict, key: str, expected_type: str) -> None:
        """Assert a property's type is ``[expected_type, \"null\"]``."""
        assert key in props, f"Missing key {key}"
        assert props[key]["type"] == [expected_type, "null"], (
            f"Expected {key}.type to be [{expected_type}, null], "
            f"got {props[key]['type']}"
        )

    def test_gga_gps_qual_is_integer(self, spec: dict[str, Any]) -> None:
        props = spec["components"]["messages"]["gga_envelope"]["payload"]["properties"]
        self._assert_type(props, "gps_qual", "integer")

    def test_gga_altitude_is_number(self, spec: dict[str, Any]) -> None:
        props = spec["components"]["messages"]["gga_envelope"]["payload"]["properties"]
        self._assert_type(props, "altitude", "number")

    def test_zda_year_is_integer(self, spec: dict[str, Any]) -> None:
        props = spec["components"]["messages"]["zda_envelope"]["payload"]["properties"]
        self._assert_type(props, "year", "integer")

    def test_alc_total_sentences_is_integer(self, spec: dict[str, Any]) -> None:
        props = spec["components"]["messages"]["alc_envelope"]["payload"]["properties"]
        self._assert_type(props, "total_sentences", "integer")

    def test_pos_x_offset_is_number(self, spec: dict[str, Any]) -> None:
        props = spec["components"]["messages"]["pos_envelope"]["payload"]["properties"]
        self._assert_type(props, "x_offset", "number")

    def test_vbw_lon_water_spd_is_number(self, spec: dict[str, Any]) -> None:
        props = spec["components"]["messages"]["vbw_envelope"]["payload"]["properties"]
        self._assert_type(props, "lon_water_spd", "number")

    def test_all_fields_are_nullable(self, spec: dict[str, Any]) -> None:
        """Every property in every per-type schema must be nullable (NMEA fields can be empty → null).

        Nullability is expressed as ``type: [T, \"null\"]`` (draft-2020-12 style)
        rather than a separate ``nullable`` keyword.
        """
        for nmea_type in documented_types():
            msg = spec["components"]["messages"][f"{nmea_type}_envelope"]
            props = msg["payload"]["properties"]
            for key, prop in props.items():
                type_val = prop.get("type")
                assert isinstance(type_val, list), (
                    f"{nmea_type}.{key}.type should be a list (nullable), got {type_val!r}"
                )
                assert "null" in type_val, (
                    f"{nmea_type}.{key}.type {type_val} does not include null"
                )


def test_spec_serializes_to_json(spec: dict[str, Any]) -> None:
    """The spec must be JSON-serializable without error."""
    json.dumps(spec)


def test_committed_spec_matches_generated(spec: dict[str, Any]) -> None:
    """Drift guard: the committed asyncapi.json must match build_spec()'s current output.

    Regenerate with ``just regenerate-spec``; CI runs this as a check.
    """
    spec_path = Path(__file__).resolve().parent.parent / "asyncapi.json"
    committed = json.loads(spec_path.read_text())
    assert committed == spec, (
        "asyncapi.json is out of date. Run 'just regenerate-spec' to refresh it."
    )
