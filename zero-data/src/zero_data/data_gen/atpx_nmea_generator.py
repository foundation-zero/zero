"""
Mock data generator for A+T (ATPX) NMEA 0183 traffic.

Publishes raw NMEA 0183 sentences to `atpx/nmea0183/<sender>/<TYPE>`, the input
the standalone `zero-atpx-nmea` service parses and republishes to
`atpx/processed/nmea/<type>/<sender>` for vector to ingest. Sentences must pass
a checksum check (or the service drops them), so payloads go through
`_sentence`, which appends the correct NMEA checksum.
"""

import logging
import random
from collections.abc import Callable
from dataclasses import dataclass

from aiomqtt import Client

from zero_data.config import MQTTConfig
from zero_data.data_gen.generator import BaseGenerator

logger = logging.getLogger(__name__)


def _checksum(body: str) -> str:
    """NMEA 0183 checksum: XOR of every byte between `$` and `*`, as hex."""
    checksum = 0
    for char in body:
        checksum ^= ord(char)
    return f"{checksum:02X}"


def _sentence(body: str) -> str:
    return f"${body}*{_checksum(body)}"


@dataclass(frozen=True)
class _NmeaSpec:
    sender: str
    sentence_type: str
    body: Callable[[], str]


def _static(body: str) -> Callable[[], str]:
    return lambda: body


# Real A+T captures (see zero-atpx-nmea/tests/test_parser.py). Simple scalar
# sentences carry a fresh reading each cycle; interdependent position/time ones
# are replayed verbatim to stay parseable.
_CORPUS: list[_NmeaSpec] = [
    _NmeaSpec("3143", "HDT", lambda: f"HEHDT,{random.uniform(0, 360):.1f},T"),
    _NmeaSpec("3143", "ROT", lambda: f"HEROT,{random.uniform(-30, 30):.1f},A"),
    _NmeaSpec(
        "3141",
        "DBT",
        lambda: (lambda m: f"SDDBT,{m * 3.281:.1f},f,{m:.1f},M,{m * 0.547:.1f},F")(
            random.uniform(2, 40)
        ),
    ),
    _NmeaSpec("3141", "DPT", lambda: f"SDDPT,{random.uniform(2, 40):.1f},0.0,21.1"),
    _NmeaSpec(
        "3145",
        "GGA",
        _static("GPGGA,104450.00,5311.41276,N,00526.15347,E,1,40,0.4,12.1,M,46.3,M,,"),
    ),
    _NmeaSpec("3145", "GLL", _static("GNGLL,5311.41276,N,00526.15347,E,104450.00,A,A")),
    _NmeaSpec("3145", "VTG", _static("GNVTG,118.99,T,115.93,M,0.06,N,0.11,K,A")),
    _NmeaSpec("3145", "ZDA", _static("GNZDA,104450.00,26,08,2026,-00,00")),
    _NmeaSpec(
        "3145",
        "RMC",
        _static(
            "GNRMC,104450.00,A,5311.41276,N,00526.15347,E,0.06,118.99,260826,3.1,E,A,S"
        ),
    ),
    _NmeaSpec("3142", "VBW", _static("VDVBW,-0.08,,A,,,V,,V,,V")),
    _NmeaSpec("3142", "VHW", _static("VDVHW,,T,,M,-0.08,N,-0.15,K")),
    _NmeaSpec("3142", "VLW", _static("VDVLW,13.79,N,13.79,N,,N,,N")),
    _NmeaSpec("3141", "ALR", _static("SDALR,,,V,V,")),
    _NmeaSpec("3141", "ALC", _static("VDALC,01,01,65,0")),
    _NmeaSpec("3142", "POS", _static("VDPOS,VD,01,A,0.0,0.0,,V,,,R")),
    _NmeaSpec("3141", "FEC", _static("PFEC,xdr,FORE,050,1")),
]


class AtpxNmeaGenerator(BaseGenerator):
    def __init__(
        self,
        interval: int | float,
        mqtt_config: MQTTConfig,
        corpus: list[_NmeaSpec] = _CORPUS,
    ):
        super().__init__(interval, mqtt_config)
        self._corpus = corpus

    async def send_messages(self, client: Client):
        logger.info(f"Sending ATPX NMEA sentences for {len(self._corpus)} types")
        for spec in self._corpus:
            payload = _sentence(spec.body())
            topic = f"atpx/nmea0183/{spec.sender}/{spec.sentence_type}"
            await client.publish(topic, payload)
