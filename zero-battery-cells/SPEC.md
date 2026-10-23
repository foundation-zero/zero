# zero-battery-cells: spec

Receives CODESYS NetVar (UDP) battery cell telemetry from the PLCs and republishes
it as one MQTT message per battery module.

## Data flow

```
PLC --UDP NetVar--> udp.rs + decoder.rs (reassembly.rs, cells.rs) --> frame queue --> mqtt.rs --> broker
                    datagram -> pack -> module frames                                JSON, QoS 1
```

Datagrams are decoded in the receive loop, straight out of the receive buffer;
the kernel socket buffer absorbs bursts. Decoded frames are fixed-size and are
serialised to JSON only at publish time. The frame queue is bounded; when full,
frames are dropped and counted (logged on the 1st and every Nth drop) rather
than stalling the receiver.
Any pipeline task ending shuts the process down so the container restarts.

## Wire format (confirmed against the bench capture)

One UDP datagram = 20-byte header + payload, all little-endian:

| Offset | Size | Field                                              |
|-------:|-----:|----------------------------------------------------|
| 0      | 8    | Preamble `00 2D 53 33 00 00 00 00` (`\0-S3`)       |
| 8      | 2    | List id (`411` = pack 41-1)                        |
| 10     | 2    | Packet index within the cycle (0-based)            |
| 12     | 2    | Variables (INTs) in this datagram                  |
| 14     | 2    | Total datagram length incl. header (must match)    |
| 16     | 4    | Cycle counter, +1 per transmission cycle           |

- A pack is larger than one datagram: the PLC sends several per cycle, up to
  128 INTs (256 bytes) each, sharing a cycle number. Fragments are buffered per
  list and concatenated in packet-index order once the declared size is reached.
  A new cycle discards any incomplete set.
- Variables are packed in declaration order, no padding, every value an
  `INT` (i16).
- Sender settings (from the PLC project exports, identical for all 22 lists):
  UDP, broadcast `255.255.255.255`, **port 50000** (the default `UDP_PORT`),
  packed variables, cyclic every 1 s, minimum gap 20 ms, no checksum, no acknowledge.
  Production forwards port 50000 with `socat UDP4-LISTEN:50000,fork,reuseaddr UDP4:<target>`
  (`socat-forward@.service`), so this service sits behind that forwarder.
- The old bench capture (`fixtures/bench-capture.bin`) was sent to port 50001
  from `192.168.102.26`; it predates the current PLC project (see open items).

## Payload layout (per pack, list id = pack number + index, `41-1` -> 411)

Declaration: `spec/KEB6_FOX_05_41_1_NVL_Declaration.txt`, a `VAR_GLOBAL` block of
`FOX_05_41_1_CellVoltage_000..671` then `FOX_05_41_1_CellTemperature_000..383`,
all `INT`; 1056 values = 2112 bytes = 9 datagrams (8x128 + 1x32).
This is the current layout: every one of the 22 per-pack declarations in the PLC
project (`PLC_PMS/cell volt and temp to vnl/split_per_instance_nvl`) is the same
shape, differing only in the name prefix. On the PLC side the values are filled
from `FOX_COMM.<pack>.oatCellVoltages[0..167].iCellVoltage_000..003` (4 per element)
and `oatCellTemperatures[0..63].iCellTemperature_000..005` (6 per element).

PLCs, packs and list ids (one list per pack, 22 in total):

| PLC  | Packs (list id)
|------|---------------------------------------------|
| KEB6 | 41-1..41-4 (411-414), 42-1..42-3 (421-423)  |
| KEB7 | 43-1..43-3 (431-433), 44-1..44-4 (441-444)  |
| KEB8 | 45-1..45-4 (451-454)                        |
| KEB9 | 46-1..46-4 (461-464)                        |

| Level  | Count | Cells per unit                     |
|--------|------:|------------------------------------|
| Pack   | 1     | 3 strings                          |
| String | 3     | 16 modules (224 V, 128 T)          |
| Module | 48    | 14 cell voltages, 8 temperatures   |

Index mapping (flat index within the voltage / temperature section):
`voltage = string*224 + module*14 + cell`, `temperature = string*128 + module*8 + probe`
(string and module 0-based here; the spreadsheet calls strings 0-2).

Units: voltages arrive as whole **millivolts** (observed ~3200-4150) and are
published in **volts**; temperatures are published as sent (whole degrees C).

## MQTT output

- Topic: `{MQTT_PREFIX}/{pack}/{string}/{module}`, e.g. `battery/41-1/2/5`;
  string and module are **1-based** (strings 1-3, modules 1-16).
- Payload: `{"pack":"41-1","string":2,"module":5,"voltages":[14 x V],"temperatures":[8 x degC]}`
- 48 messages per pack per cycle, QoS 1, not retained.
- Shorter declarations are accepted: the undeclared tail is zero-padded so every
  module still gets a frame.

## Configuration (environment)

| Variable                    | Default     | Notes                                            |
|-----------------------------|-------------|--------------------------------------------------|
| `NVL_FILE`                  | required    | template declaration (one pack); the other packs are derived from it |
| `OWN_LIST_IDS`              | all 22 known| JSON array, e.g. `[411, 413]`; must be known list ids; a redundant replica runs the others |
| `UDP_PORT`                  | 50000       | matches the PLC project                          |
| `MQTT_HOST` / `MQTT_PORT`   | localhost / 1883 |                                             |
| `MQTT_PREFIX`               | `battery`   | first topic segment                              |
| `MQTT_USERNAME`/`PASSWORD`  | none        | both must be non-empty to be used                |

The template is validated at startup (INT-only, name/list id consistent, not
larger than a full pack) and then re-prefixed for each of the 22 known list ids
(`mapping::KNOWN_PACKS`), e.g. `FOX_05_41_1_...` -> `FOX_05_46_3_...`.
Replicas split the lists via `OWN_LIST_IDS`.

## Tooling

- `zero-battery-cells run` (default): the pipeline.
- `zero-battery-cells dissect [--file F]`: print the topics a datagram stream
  would publish, without MQTT. Recording format: repeated `u32 LE length + datagram`.
- `fixtures/sample-recording.bin`: synthetic full pack (9 datagrams, 48 topics).
- `fixtures/bench-capture.bin`: two real cycles from the bench (8 datagrams).

## Open items

1. **The bench capture is outdated, the declaration is current.** The capture
   carries 452 INTs per cycle (4 datagrams: 3x128 + 68 = 904 bytes) on port 50001,
   while the current PLC project sends 1056 INTs (2112 bytes) on port 50000. Fed
   with the capture, the service never completes a pack and only logs
   `cycle N incomplete (904 of 2112 bytes)`. Take a fresh capture from the
   deployed PLCs to confirm the 9-datagram layout and the preamble.
2. All payload values in the capture are zero except the first (`0xABCD`, a
   marker), so unit/scale of temperatures and the cell ordering are unverified
   on real data.
3. Not wired up yet: CI workflow and Helm chart (the service exists only in
   `docker-compose.yml`, profile `battery-cells`).
