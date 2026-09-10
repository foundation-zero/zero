"""Builds the AsyncAPI 3.0.0 spec for zero-atpx-nmea: the consumer contract for
its MQTT interface.

``build_spec()`` returns the full AsyncAPI document (ready to serialise as
``asyncapi.json``) describing the raw NMEA input channel and one output channel
per documented sentence type, each with its JSON envelope schema. The result is
guaranteed to match what the service actually publishes.

Each schema is derived by parsing a real example sentence and reading its fields.
"""

from decimal import Decimal
from typing import Any

import pynmea2

from zero_atpx_nmea.corpus import documented_types, sender_for, sentence_for
from zero_atpx_nmea.parser import parse

# Envelope keys that are always added by parser.py itself (not from pynmea2
# field declarations), mapped to their JSON Schema types.
_SPECIAL_FIELD_TYPES: dict[str, str] = {
    "type": "string",
    "sender": "string",
    "talker": "string",
    "raw": "string",
    "latitude": "number",
    "longitude": "number",
    "manufacturer": "string",
    "data": "array",
    "nmea_time": "string",
}
_NMEA_PREFIXED_FIELDS = {"type", "sender", "talker", "raw", "table"}


def _json_type_from_converter(converter: Any) -> str:
    """Map a pynmea2 field converter to its AsyncAPI JSON Schema type."""
    if converter is None:
        return "string"
    if converter is int:
        return "integer"
    if converter is float or converter is Decimal:
        return "number"
    # timestamp/datestamp converters yield datetimes the parser serialises as strings.
    return "string"


def _converter_type_for_field(field_name: str, msg_type: type) -> str | None:
    """JSON Schema type for the pynmea2-declared converter of *field_name*, or None.

    *field_name* is the original pynmea2 field name, not the (possibly renamed)
    envelope key.
    """
    if not hasattr(msg_type, "name_to_idx"):
        return None
    for _, name, *rest in msg_type.fields:
        if name == field_name:
            converter, *_ = rest or [None]
            return _json_type_from_converter(converter)
    return None


def _gather_envelope_for_type(nmea_type: str) -> dict[str, str]:
    """Return the envelope key → JSON Schema type map for a documented type.

    Keys are in the order ``parse()`` emits them. Runs the real ``parse()`` on the
    corpus example for the authoritative envelope, then enriches types from
    pynmea2's declared converters.
    """
    sender = sender_for(nmea_type)
    raw = sentence_for(nmea_type)
    topic = f"atpx/nmea0183/{sender}/{nmea_type.upper()}"
    envelope = parse(raw, topic)
    if envelope is None:
        raise ValueError(f"Corpus example sentence for {nmea_type} failed to parse")

    msg = pynmea2.parse(raw, check=True)
    msg_type = type(msg)

    # Map each envelope key back to its original pynmea2 field name, so the
    # declared converter stays findable for fields parser.py renamed.
    names = [name for _, name, *_ in msg_type.fields]
    orig_name_by_env_key = (
        {name: name for name in names}
        | {"nmea_time": name for name in names if name == "timestamp"}
        | {f"nmea_{name}": name for name in names if name in _NMEA_PREFIXED_FIELDS}
    )

    def type_for(env_key: str) -> str:
        if env_key in _SPECIAL_FIELD_TYPES:
            return _SPECIAL_FIELD_TYPES[env_key]
        orig = orig_name_by_env_key.get(env_key)
        return (_converter_type_for_field(orig, msg_type) if orig else None) or "string"

    return {env_key: type_for(env_key) for env_key in envelope}


def _json_pointer_ref(channel_id: str) -> str:
    """Build a ``#/channels/<id>`` JSON Pointer ``$ref`` for a channel.

    Encodes the id segment per RFC 6901 (``~``→``~0``, ``/``→``~1``); braces are
    percent-encoded because some AsyncAPI tools treat them specially in $refs.
    """
    segment = channel_id.replace("~", "~0").replace("/", "~1")
    segment = segment.replace("{", "%7B").replace("}", "%7D")
    return f"#/channels/{segment}"


def _build_properties(field_types: dict[str, str]) -> dict[str, Any]:
    """Build the ``properties`` dict for an object schema.

    Every property is nullable, since empty NMEA fields parse to ``null``.
    """
    return {
        key: {"type": [json_type, "null"]} for key, json_type in field_types.items()
    }


def _build_message_schema(
    nmea_type: str, field_types: dict[str, str]
) -> dict[str, Any]:
    """Build a per-type message schema."""
    return {
        "name": f"{nmea_type}_envelope",
        "title": f"{nmea_type.upper()} envelope",
        "description": f"Parsed payload for NMEA 0183 {nmea_type.upper()} sentence type",
        "contentType": "application/json",
        "payload": {
            "type": "object",
            "properties": _build_properties(field_types),
            "required": list(field_types),
        },
    }


def build_spec(*, include_input_channel: bool = True) -> dict[str, Any]:
    """Build the AsyncAPI 3.0.0 document for zero-atpx-nmea's MQTT interface.

    With ``include_input_channel=False`` the raw NMEA input channel is omitted,
    leaving only the JSON output channels. The raw channel carries a bare-string
    payload on A+T's broker; consumers that build a schema from object fields
    (e.g. the MQTT-GraphQL bridge) can't use it, so they take the output-only
    view. The default is the full contract, as committed to ``asyncapi.json``.
    """
    # Static, not the hatch-vcs package version: that changes every commit and
    # would churn asyncapi.json on every push. Bump when the documented
    # interface (channels, schemas) changes.
    version = "0.1.0"

    spec: dict[str, Any] = {
        "asyncapi": "3.0.0",
        "info": {
            "title": "Zero ATPX NMEA",
            "version": version,
            "description": (
                "Zero ATPX NMEA bridges A+T's raw NMEA 0183 stream onto our own MQTT "
                "broker. It subscribes to `atpx/nmea0183/<sender>/<TYPE>` on "
                "**A+T's onboard broker** (the ATPX MQTT host), parses each sentence "
                "with pynmea2 into a JSON envelope, and republishes it to "
                "`atpx/processed/nmea/<type>/<sender>` on **our own MQTT broker** "
                "(the output MQTT host).\n\n"
                "**Known-type scope.** The documented type set below is the "
                "known/supported subset for which this service has been tested with "
                "real A+T data. The service subscribes to `atpx/nmea0183/#` and parses "
                "any type pynmea2 or our registered custom parsers support, including "
                "types not listed here \u2014 an undocumented type carries whatever fields "
                "pynmea2 produces rather than a curated schema, while unparseable "
                "sentences are dropped. Adding a new documented type is a one-line corpus "
                "addition plus a spec regeneration."
            ),
        },
        "channels": {},
        "operations": {},
        "components": {
            "messages": {},
        },
    }

    if include_input_channel:
        _add_input_channel(spec)

    for nmea_type in documented_types():
        field_types = _gather_envelope_for_type(nmea_type)
        message_id = f"{nmea_type}_envelope"
        channel_id = f"atpx/processed/nmea/{nmea_type}/{{sender}}"

        spec["channels"][channel_id] = {
            "address": channel_id,
            "title": f"{nmea_type.upper()} processed envelope",
            "description": (
                f"Parsed JSON envelope for NMEA 0183 {nmea_type.upper()} sentences. "
                "``{sender}`` identifies the originating A+T device."
            ),
            "parameters": {
                "sender": {
                    "description": "A+T device identifier (e.g. 3143, 3145)",
                    "location": "$message.header#/topic/parts/4",
                },
            },
            "messages": {
                message_id: {"$ref": f"#/components/messages/{message_id}"},
            },
        }
        spec["components"]["messages"][message_id] = _build_message_schema(
            nmea_type, field_types
        )
        spec["operations"][f"send_{nmea_type}_envelope"] = {
            "action": "send",
            "channel": {"$ref": _json_pointer_ref(channel_id)},
        }

    return spec


def _add_input_channel(spec: dict[str, Any]) -> None:
    """Add the raw NMEA input channel, its message, and its receive operation."""
    input_channel_id = "atpx/nmea0183/{sender}/{TYPE}"
    spec["channels"][input_channel_id] = {
        "address": input_channel_id,
        "title": "Raw NMEA 0183 input from A+T broker",
        "description": (
            "Raw NMEA 0183 sentences published by A+T's onboard systems. "
            "``{sender}`` identifies the A+T device (e.g. ``3143``, ``3145``), "
            "``{TYPE}`` is the uppercase NMEA 0183 sentence type "
            "(e.g. ``ROT``, ``GGA``)."
        ),
        "parameters": {
            "sender": {
                "description": "A+T device identifier (e.g. 3143, 3145, 3141, 3142)",
                "location": "$message.header#/topic/parts/2",
            },
            "TYPE": {
                "description": "Uppercase NMEA 0183 sentence type (e.g. ROT, GGA, RMC)",
                "location": "$message.header#/topic/parts/3",
            },
        },
        "messages": {
            "raw_nmea_sentence": {
                "$ref": "#/components/messages/raw_nmea_sentence",
            },
        },
    }
    spec["components"]["messages"]["raw_nmea_sentence"] = {
        "name": "raw_nmea_sentence",
        "title": "Raw NMEA 0183 sentence",
        "description": "A single raw NMEA 0183 sentence as received from A+T",
        "contentType": "text/plain",
        "payload": {
            "type": "string",
            "description": "Raw NMEA 0183 sentence string, e.g. ``$GPGGA,...*hh``",
        },
    }
    spec["operations"]["receive_raw_nmea"] = {
        "action": "receive",
        "channel": {
            "$ref": _json_pointer_ref(input_channel_id),
        },
    }
