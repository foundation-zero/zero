"""Custom pynmea2 sentence classes for standard IEC 61162-1 / NMEA 0183
sentence types that pynmea2 (as of 1.19.0) does not implement.

Importing this module is enough to register these classes: pynmea2's
`NMEASentenceType` metaclass auto-registers every `TalkerSentence` subclass
into `TalkerSentence.sentence_types` by class name at class-definition time
(see `pynmea2/nmea.py`), which is exactly the lookup `pynmea2.parse()` uses.
So `parser.py` only needs to `import zero_atpx_nmea.custom_sentences` once,
before parsing, for these types to flow through the same generic envelope
logic as every pynmea2-native sentence.

Confirmed pynmea2 doesn't already define these (checked against pynmea2
1.19.0's `TalkerSentence.sentence_types`) — see PR discussion for A+T's live
NMEA stream, which carries these three at low frequency.
"""

import pynmea2
from pynmea2.nmea_utils import timestamp


class ALR(pynmea2.TalkerSentence):
    """Set alarm state.

    IEC 61162-1 / NMEA 0183 standard sentence. Field layout confirmed from
    multiple independent secondary sources (e.g. Actisense's NMEA 0183
    field-reference sheet; installation manuals quoting IEC 61162-1 §8.3.15,
    "ALR – Set alarm state") which agree on this 5-field layout:

        $--ALR,hhmmss.ss,xxx,A,A,c--c*hh

    Captured sample: ``$SDALR,,,V,V,*64`` (5 fields, all but condition/ack
    empty) — field count/order matches.
    """

    fields = (
        ("Time of alarm condition change (UTC)", "timestamp", timestamp),
        # Alarm identifier at the source. Documented as numeric ("xxx",
        # 000-999) by some sources, but other captured real-world sentences
        # (e.g. "$RAALR,220516,BPMP1,A,A,Bilge pump alarm1*43") show
        # alphanumeric mnemonics in this position, so it's left untyped
        # rather than forced through an `int` converter.
        ("Local alarm number/identifier", "alarm_number"),
        ("Alarm condition (A=threshold exceeded, V=not exceeded)", "alarm_condition"),
        (
            "Alarm acknowledge state (A=acknowledged, V=unacknowledged)",
            "alarm_ack_state",
        ),
        ("Alarm description text", "alarm_text"),
    )


class ALC(pynmea2.TalkerSentence):
    """Cyclic alert list.

    IEC 61162-1 §8.3.13. Reports how many IEC 62923 alerts are currently
    active, split (if needed) across multiple ALC sentences, each carrying
    up to a handful of repeating alert-identifier groups:

        $--ALC,xx,xx,xx,x,aaa,x.x,x.x,x.x,...*hh

    Field layout (the 4 fixed fields) confirmed via the go-nmea library's
    ALC implementation (https://github.com/adrianmo/go-nmea/blob/master/alc.go),
    itself sourced from a FURUNO FAR-15xx radar installation manual quoting
    the IEC 61162-1 format. Only the 4 fixed fields are declared here: the
    repeating (manufacturer_mnemonic, alert_id, alert_instance, revision)
    groups that would follow when `num_alerts` > 0 aren't representable in
    pynmea2's fixed positional `fields` tuple, and A+T's captured sample has
    zero alert entries, so no repeating group is observed on the wire.

    Captured sample: ``$VDALC,01,01,65,0*6F`` (4 fields) — field count/order
    matches.
    """

    fields = (
        ("Total number of ALC sentences in this message", "total_sentences", int),
        ("Sentence number within this message", "sentence_number", int),
        ("Sequential message identifier", "sequence_id", int),
        ("Number of alert entries in this sentence", "num_alerts", int),
    )


class POS(pynmea2.TalkerSentence):
    """Device position and ship dimensions report or configuration command.

    IEC 61162-1 §8.3.76 (added/revised in edition 6.0, 2024). The official
    title was confirmed from the IEC 61162-1:2024 table of contents, but the
    body text (§8.3.76, p.100) sits behind IEC's paywall and wasn't
    reachable — no field-by-field public breakdown of this specific,
    low-usage sentence was found. Field NAMES below are therefore a
    best-effort reconstruction from the sentence's stated purpose ("device
    position and ship dimensions") and general IEC 61162-1 conventions
    (an offset triple followed by a validity flag; a trailing
    report/command status letter), not a verified-against-the-standard
    layout — treat them as informative, not authoritative.

    What IS verified against the captured sample is the field COUNT and
    ORDER, which is what the generic envelope actually depends on:

        $VDPOS,VD,01,A,0.0,0.0,,V,,,R*08

    -> talker=VD, equipment_number=01, status=A, x=0.0, y=0.0, z=<empty>,
       position_valid=V, length=<empty>, beam=<empty>, sentence_status=R
    """

    fields = (
        ("Talker ID of the reporting/configured device", "device_talker"),
        ("Equipment number", "equipment_number", int),
        ("Sentence status flag", "status"),
        ("X offset from reference point, metres", "x_offset", float),
        ("Y offset from reference point, metres", "y_offset", float),
        ("Z offset from reference point, metres", "z_offset", float),
        ("Position validity (A=valid, V=invalid)", "position_valid"),
        ("Ship length, metres", "length", float),
        ("Ship beam, metres", "beam", float),
        ("Report/command status (e.g. R=report, C=command)", "sentence_status"),
    )
