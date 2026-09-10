"""Tests for the self-validating NMEA sentence corpus."""

from typing import Any

from zero_atpx_nmea.corpus import documented_types, sender_for, sentence_for
from zero_atpx_nmea.parser import parse


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
