"""Documented NMEA 0183 type → representative example sentence.

The authoritative list of types `zero-atpx-nmea` documents in its AsyncAPI spec.
Each entry pairs a lowercased type key with a real, parseable sentence captured
from A+T's stream, from which the spec builder derives per-type payload schemas.
Adding a type: add a line here, regenerate the spec.
"""

from typing import NamedTuple


class CorpusEntry(NamedTuple):
    sender: str
    sentence: str


_CORPUS: dict[str, CorpusEntry] = {
    "rot": CorpusEntry("3143", "$HEROT,000.1,A*2A"),
    "hdt": CorpusEntry("3143", "$HEHDT,199.1,T*2F"),
    "fec": CorpusEntry("3141", "$PFEC,xdr,FORE,050,1*64"),
    "gga": CorpusEntry(
        "3145",
        "$GPGGA,104450.00,5311.41276,N,00526.15347,E,1,40,0.4,12.1,M,46.3,M,,*5E",
    ),
    "dbt": CorpusEntry("3141", "$SDDBT,23.7,f,7.2,M,3.9,F*3F"),
    "dpt": CorpusEntry("3141", "$SDDPT,7.2,0.0,21.1*62"),
    "gll": CorpusEntry("3145", "$GNGLL,5311.41276,N,00526.15347,E,104450.00,A,A*76"),
    "vtg": CorpusEntry("3145", "$GNVTG,118.99,T,115.93,M,0.06,N,0.11,K,A*3C"),
    "vbw": CorpusEntry("3142", "$VDVBW,-0.08,,A,,,V,,V,,V*7D"),
    "zda": CorpusEntry("3145", "$GNZDA,104450.00,26,08,2026,-00,00*5B"),
    "vhw": CorpusEntry("3142", "$VDVHW,,T,,M,-0.08,N,-0.15,K*4B"),
    "vlw": CorpusEntry("3142", "$VDVLW,13.79,N,13.79,N,,N,,N*5F"),
    "rmc": CorpusEntry(
        "3145",
        "$GNRMC,104450.00,A,5311.41276,N,00526.15347,E,0.06,118.99,260826,3.1,E,A,S*51",
    ),
    "alr": CorpusEntry("3141", "$SDALR,,,V,V,*64"),
    "alc": CorpusEntry("3141", "$VDALC,01,01,65,0*6F"),
    "pos": CorpusEntry("3141", "$VDPOS,VD,01,A,0.0,0.0,,V,,,R*08"),
}


def documented_types() -> list[str]:
    """Return the list of documented type names in insertion order."""
    return list(_CORPUS.keys())


def sender_for(nmea_type: str) -> str:
    """Return the representative sender for a documented type."""
    return _CORPUS[nmea_type].sender


def sentence_for(nmea_type: str) -> str:
    """Return the representative example sentence for a documented type."""
    return _CORPUS[nmea_type].sentence
