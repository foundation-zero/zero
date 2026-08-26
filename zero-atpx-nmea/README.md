# Zero ATPX NMEA

Subscribes to A+T's `atpx/nmea0183/<sender>/<TYPE>` topics (raw NMEA 0183
sentences), parses each sentence with `pynmea2` into a JSON envelope, and
republishes it to `atpx/processed/nmea/<type>/<sender>` on our own MQTT
broker. Vector then ingests `atpx/processed/nmea/#` into Greptime tables
named `atpx__nmea_<type>`; this service never touches Greptime directly.

The parser (`zero_atpx_nmea.parser.parse`) is a pure function — no I/O — and
is the primary tested seam: it maps every pynmea2 field through its declared
type converter (so numbers are floats/ints, not strings), turns empty NMEA
fields into `null`, and adds decimal `latitude`/`longitude` for position
sentences (GGA/GLL/RMC). Sentences that fail checksum verification or can't
be parsed are dropped (and logged by the caller), never raised.

The FastStream MQTT app (`zero_atpx_nmea.app`) is a thin, untested shell
around that function: it uses two separate brokers, since in production
`ATPX_MQTT_HOST` (A+T's onboard broker, unauthenticated) differs from
`MQTT_HOST` (our own broker); locally both resolve to the same `vernemq`.

See `PLAN.md` (one directory up) for the full spec.

Otherwise this follows standard project conventions.
