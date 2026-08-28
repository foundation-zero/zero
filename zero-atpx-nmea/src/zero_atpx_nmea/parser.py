"""Pure NMEA 0183 sentence → JSON envelope parser.

This is the primary seam of the service: a pure function with no I/O, so it
can be unit-tested with no broker. The FastStream app in :mod:`zero_atpx_nmea.app`
is a thin shell around :func:`parse`.
"""

import datetime
from decimal import Decimal
from typing import Any

import pynmea2

# Registers custom sentence classes (ALR/ALC/POS) that pynmea2 itself
# doesn't define, so `pynmea2.parse()` below picks them up like any other
# TalkerSentence subclass. Import is for its registration side effect only.
import zero_atpx_nmea.custom_sentences  # noqa: F401

# Envelope keys we always set ourselves (from the topic/sentence, not from a
# parsed NMEA field). A parsed field whose name collides with one of these
# is renamed to `nmea_<name>` so it can never be silently overwritten.
_RESERVED_KEYS = {"type", "sender", "talker", "raw", "table"}


def _envelope_key(field_name: str) -> str:
    """Map a pynmea2 field name to its envelope key.

    `timestamp` is renamed to `nmea_time`: Vector's route transform sets a
    top-level `.timestamp` to the ingestion time (the Greptime time index),
    and several sentences (GGA/GLL/RMC/ZDA) have a field literally named
    `timestamp` (the NMEA time-of-day) which would otherwise collide with
    and be silently overwritten by that.

    Any other field name that collides with an envelope-reserved key
    (`type`/`sender`/`talker`/`raw`/`table`) is similarly prefixed, so a
    future/unexpected sentence field can never shadow those.
    """
    if field_name == "timestamp":
        return "nmea_time"
    if field_name in _RESERVED_KEYS:
        return f"nmea_{field_name}"
    return field_name


def _jsonable(value: Any) -> Any:
    """Convert a pynmea2-produced field value into a JSON-serializable primitive."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    return value


def parse(raw_sentence: str, topic: str) -> dict[str, Any] | None:
    """Parse one NMEA 0183 sentence captured on `topic` into a JSON-able dict.

    `topic` is expected to be `atpx/nmea0183/<sender>/<TYPE>`; `sender` and
    the lowercased `TYPE` become the envelope's `sender`/`type`.

    Parses with checksum verification on. Returns `None` (never raises) when
    the sentence fails checksum verification or otherwise can't be parsed —
    the caller is responsible for logging the drop.
    """
    parts = topic.split("/")
    if len(parts) < 4 or parts[0] != "atpx" or parts[1] != "nmea0183":
        return None
    sender, sentence_type = parts[-2], parts[-1]
    envelope_type = sentence_type.lower()

    try:
        msg = pynmea2.parse(raw_sentence, check=True)
    except pynmea2.ParseError:
        return None

    envelope: dict[str, Any] = {}

    for name, idx in type(msg).name_to_idx.items():
        raw_value = msg.data[idx] if idx < len(msg.data) else ""
        if raw_value == "":
            value: Any = None
        else:
            try:
                value = getattr(msg, name)
            except (ValueError, TypeError):
                value = None
        envelope[_envelope_key(name)] = _jsonable(value)

    if hasattr(msg, "latitude"):
        try:
            envelope["latitude"] = _jsonable(msg.latitude)
            envelope["longitude"] = _jsonable(msg.longitude)
        except (ValueError, TypeError):
            envelope["latitude"] = None
            envelope["longitude"] = None

    if isinstance(msg, pynmea2.ProprietarySentence):
        # Generic proprietary sentence (e.g. $PFEC): no declared field spec,
        # so expose whatever pynmea2 gives us verbatim.
        envelope["manufacturer"] = msg.manufacturer
        envelope["data"] = list(msg.data)

    envelope["type"] = envelope_type
    envelope["sender"] = sender
    envelope["talker"] = getattr(msg, "talker", None)
    envelope["raw"] = raw_sentence

    return envelope
