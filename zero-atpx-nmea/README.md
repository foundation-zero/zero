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

## Consumer contract (AsyncAPI specification)

The service's MQTT interface is documented in a committed **AsyncAPI 3.0.0**
specification at [`asyncapi.json`](./asyncapi.json). It describes:

- **Input** — the `atpx/nmea0183/{sender}/{TYPE}` channel where A+T publishes
  raw NMEA 0183 sentences (string payload).
- **Output** — one channel per documented sentence type,
  `atpx/processed/nmea/<type>/{sender}`, each with a concrete per-type JSON
  envelope schema.

Vector's NMEA ingestion pipeline depends on these output channels; the spec
is the contract for anyone building on top of the `atpx__nmea_<type>`
Greptime tables.

### Regenerating

```sh
just regenerate-spec
```

Updates `asyncapi.json` from the current parser and corpus. CI runs this
same command and fails if the committed file would change, so the contract
never silently drifts from what the service actually emits.

### Viewing

```sh
uv run python -m zero_atpx_nmea asyncapi
```

Prints the spec to stdout.

