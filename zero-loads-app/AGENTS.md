# Loads app: agent notes

Read the repository's [CODESTYLE.md](../CODESTYLE.md) first. This file collects the context that is
not obvious from the code: where the data comes from and how to look at live data. The
[README](README.md) covers running the app.

## Sources of truth

- **The loads Google Sheet** (`11sE_LaWqBz4rfQrQgS-j8XIEl9pCgsJEX_HSi0XDoxw`) holds the technical
  names, the max loads (lower and upper warning and alarm thresholds) and the SailPack mapping. It
  is edited in meetings with the rigging and naval team, so code follows the sheet, not the other
  way round.
- **The registry** (`src/loads/registry/registry.py`, built from the models in
  `src/loads/sensors/`) is the source of truth for which variables the app reads and from which MQTT
  topic and payload path.
- **The SailPack load cases** (`src/sailpack/load_cases/*.htm`) give the target loads. Every load
  case is modelled on port tack; the starboard tack is a ps↔sb mirror.

## Sheet workflow

The seed commands download the sheet tabs (`LoadsSheet` in `src/loads/registry/sheets.py`)
directly; there are no CSV copies in the repo.

```bash
just export_seed                          # download, check and regenerate the seeds and the conflicts CSV
just check_seed                           # download, check and compare with the committed seeds; also in CI
```

Both first check the sheet: technical names against the registry and numeric and ordered
thresholds. A sheet edit can therefore turn CI red until the seeds are regenerated. The live sheet
is also checked by `tests/integration/test_loads_sheet.py`. To change the sheet, produce a CSV and
let the user import it into the tab with "replace current sheet" (keeps the gid). The claude.ai Google Drive connector
is not authenticated, so a session cannot edit the sheet.

- **Max loads** are read by header name (`src/sailpack/max_loads.py`). The runner block thresholds
  are not in the sheet; they are derived from the runner tail thresholds with the Vitters PLC
  factors (`RUNNER_BLOCK_LOAD_PER_TAIL_LOAD` in `src/sailpack/seed_utils.py`).
- **Seeds**: SailPack targets go into `loads.reference_values`, the max loads into
  `loads.thresholds`. Targets outside their thresholds are clamped to the warning, or to the alarm
  where that side has no warning (the DB CHECK constraints require
  `alarm_low ≤ warning_low ≤ target ≤ warning_high ≤ alarm_high`), and listed in
  `src/sailpack/target_threshold_conflicts.csv`.

## Live MQTT data

- The sail system PLC publishes through the sail-system MQTT adapter to the broker at
  `rabbitmq-zero.tail0b4840.ts.net:1883` (over Tailscale), on `sail-systems/<function block>`.
  Payloads are flat JSON with `/`-separated keys (`st_Load/i_Load`), which the models'
  `validation_alias` matches. Loads are in 10 kg; the app converts to tonnes.
- The adapter only publishes when the PLC is up. When it is down, only
  `sail-systems/sail-system-mqtt-adapter/alive` comes through. Not every topic is published within
  a few minutes (on 2026-10-08, 31 of the data map's 74 came through in 4 minutes), so use the data map below for
  the full structure.
- The adapter's data map, port-forwarded from the cluster to `http://localhost:8080`, shows every
  topic with its fields, current values and the PLC descriptions. Port 8080 is also Hasura's local
  port, so only one of the two can run at a time.
- `tools/sail-system-mqtt/mqtt_schema_compare.py` records the topics and payload schema
  (`sail-system-mqtt-schema.json`) and compares them with an earlier recording.
- Before changing a payload path, check that the field is on live MQTT: a missing field fails the
  whole topic's validation, so every variable on that topic goes missing.
