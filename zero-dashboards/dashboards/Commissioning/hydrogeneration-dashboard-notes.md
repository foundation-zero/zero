# Hydrogeneration dashboard — data notes & open questions

Working notes for the new sea-trial hydrogeneration dashboard (branch
`feature/hydrogeneration-dashboard`). Captures what's confirmed against the
live GreptimeDB (`greptime-zero.tail0b4840.ts.net:4000`) and the repo, plus
everything that still needs an answer from the PCS/Marpower engineer or A+T
rigger before the dashboard can be finished. Not a dashboard spec — a build
plan and a checklist to take to the right person.

This dashboard runs against **live production data**, not the commissioning
test-PLC rig (`prop_test__data` / `devices__can_aradex.*` in Postgres) used
by `propulsion-test-dashboard.json`. That dashboard was only a layout
reference — the underlying data source is different and won't be available
going forward.

---

## 1. PCS data — `public.marpower__150000_propulsion*` (GreptimeDB)

21 tables exist under this prefix. Row shape: every `<measure>__value` /
`__is_valid` / `__has_value` / `__timestamp` clump is populated on **every
row** (confirmed by sampling live data) — these are dense per-scan-cycle
snapshots, not sparse per-measure updates. A plain `ORDER BY timestamp DESC
LIMIT 1` gives a real, complete snapshot; no forward-fill logic needed.

### Tables to use

| Table | Purpose |
|---|---|
| `marpower__150000_propulsion__pcs_fwd` / `pcs_aft` | Per-pod PCS aggregate |
| `marpower__150000_propulsion__pcs_{fwd,aft}_ara1` / `ara2` | Per-drive Aradex telemetry (2 drives per pod) |
| `marpower__150000_propulsion__pcs_{fwd,aft}_pshelm` / `sbhelm` | Helm-station levers + mode buttons (port/starboard station, covers both pods) |

### Tables *not* to use (yet)

`marpower__150000_propulsion` (bare, no suffix) and
`marpower__150000_propulsion_general` — column sets look like a union of
several distinct source topics (PCS + Aradex + helm fields all present
together, no pod-distinguishing column). Treat as legacy/catch-all until
confirmed otherwise. **Default plan: compute "Total power" / "Total torque"
as fwd + aft ourselves, rather than trust these tables.**

### Field mapping (what we found for each requested datapoint)

| Requested field | Source | Column(s) | Confidence |
|---|---|---|---|
| Mode (Gen/Prop/Man/Motorsail/Free) | `pcs_{fwd,aft}` | `propellor_sailing_mode__value` (BIGINT, 5 distinct values seen live: 0–4) | Values confirmed to exist; **labels unknown — see open questions** |
| Pitch | `pcs_{fwd,aft}` | `propellor_pitch__value` | High |
| Azimuth | `pcs_{fwd,aft}` | `propellor_azimuth__value` | High |
| Lever setting | `pcs_{fwd,aft}_pshelm/sbhelm` | `{aft,fwd}_thruster_lever_speed_signal__value`, `..._lever_azimuth_{1,2}_signal__value` | High — **excluded from v1 per your instruction** |
| Torque — Aradex | `pcs_{fwd,aft}_ara{1,2}` | `torque__value` (per drive; 2 per pod) | High |
| Torque — Shear beam | `pcs_{fwd,aft}` | `shear_beam_calculated__value` (raw: `shear_beam_1..4__value`) | High |
| Torque — Randax (electric motor) | `pcs_{fwd,aft}` | `motor_torque__value` | High |
| Power — Aradex | `pcs_{fwd,aft}_ara{1,2}` | `power__value` (per drive) | High |
| Power — Randax/motor | `pcs_{fwd,aft}` | `motor_power_in_perc__value` — **percentage, not kW; needs rated power to convert** | Medium |
| RPM — Aradex | `pcs_{fwd,aft}_ara{1,2}` | `speed__value` (per drive, electrical) | High |
| RPM — prop shaft (aggregate) | `pcs_{fwd,aft}` | `output_velocity__value` | Medium — need engineer confirmation this is shaft RPM and not something else |
| RPM/torque setpoint (regen) | `pcs_{fwd,aft}` | `speed_setpoint__value`, `reference_frequency__value` | Medium — unclear which is which |
| Regen control mode (Torque/RPM) | `pcs_{fwd,aft}_ara{1,2}` | `speed_or_torque_setpoint__value` — **typed BOOLEAN, not a magnitude** | Confirmed live: only `false`/`null` observed so far. You're already asking engineering to change this to a real setpoint value — until then this can only render as a 2-state flag, no setpoint trace |
| Setpoint-not-reached flags | `pcs_{fwd,aft}` | `pitch_setpoint_not_reached`, `rpm_setpoint_not_reached`, `azimuth_setpoint_not_reached` (BOOLEAN) | High |
| Randax/motor housekeeping | `pcs_{fwd,aft}` (tail columns) | `bearing_de_temp`, `bearing_nde_temp`, `windingtempu/v/w_1/2`, `venttemp_1/2`, `heatingonoff`, `comalarm`, `waterleakalarm` | High — these appear to be Randax electric-motor protection IO, appended onto the same PCS table |
| "Total power" / "Total torque" (top-level) | Computed | `fwd.<source> + aft.<source>` for whichever torque/power source is chosen as canonical | Pending — see open questions |

### Mode inference attempt (didn't resolve it)

Tried correlating `propellor_sailing_mode__value` against the helm-station
`man_mode_selected_{aft,fwd}_thruster` / `prop_mode_selected_...` /
`reg_mode_selected_...` booleans (`pcs_aft_pshelm`), bucketed to 5-second
windows over the last 30 days. **All three "*_selected" flags were `false`
in every bucket for every mode value** — so these feedback bits haven't
actually gone true in that window, and can't be used to infer the mapping.

Distribution of `propellor_sailing_mode__value` over 30 days: `0` dominates
(429k samples), `1` next (96.5k), `2`/`3`/`4` are rare (≤2k, only 16 for
`4`) — consistent with `0` being idle/Free and the rest being active states,
but **not enough to safely assign labels**.

---

## 2. A+T instrument data — two independent paths in GreptimeDB

### Path A (recommended): `public.atpx_raw` — A+T's raw instrument bus

This is the "raw table" route you mentioned, and it's the better one. A+T
publishes one float per message on its own MQTT broker as
`atpx/<field-id>/<sender*256+instance>` (see `vector/processing/atpx_0_consts.vrl`
for the full ~300-entry field-id → name dictionary and the sender-id → name
table). Vector lands every message as one row in a single **long/EAV-format**
table:

```
atpx_raw(timestamp, topic, sender, field, value)
```

Confirmed live and populated (checked over the last 10 minutes) for
everything on your list:

| Field you need | `field` value | Senders seen live |
|---|---|---|
| AWA | `app_wind_angle` | `atprocessor_0`, `wind_board_1`, `wind_board_3`, `wind_board_4` |
| AWS | `app_wind_speed_kts` | `atprocessor_0`, `wind_board_1/3/4/5`, `fastnet_5` |
| TWA | `true_wind_angle` | `atprocessor_0`, `wind_board_1/3/4/5`, `fastnet_5` |
| TWS | `true_wind_speed_kts` | `atprocessor_0`, `wind_board_1/4/5`, `fastnet_5` |
| Heel | `heel_angle_deg` | `atprocessor_0`, `main_interface_board_0` |
| Rudder | `rudder_angle_deg` | `atprocessor_0`, `autopilot_0`, `fastnet_5` (`port_rudder_angle_deg` exists in the dictionary but has **no live data** — presumably single-rudder boat) |
| Leeway | `leeway` (`atprocessor_0` only) / `signed_leeway` (`atprocessor_0`, `wind_board_1/3/4/5`) | see above |
| BSP | `boat_speed_kts` | `speed_board_1/2`, `atprocessor_0`, `nmea0183_70`, `fastnet_5` |

**`atprocessor_0` publishes every one of these fields** — it looks like A+T's
own fused/processed output (their internal sensor-fusion engine, distinct
from the individual raw instrument boards). **Recommended default: use
`sender = 'atprocessor_0'` uniformly** as the single canonical series per
field, rather than picking a specific board — but confirm with A+T/PCS
engineer this is actually the certified/primary feed on this boat and not
just one of several redundant paths.

**Gotcha:** `atpx_raw` is high-volume (every field, every sender, one row per
message). An unfiltered query without a tight time bound timed out even at
60s for a 2-day window; a 10-minute window with a `field =` filter returned
in ~100ms. **Always filter tightly on time and `field`/`sender`** — the
dashboard's own time-range picker does this naturally via `$__timeFilter`,
but ad-hoc exploration needs care, and the pitch/power scatter's averaging
query (below) should bucket before joining, not join raw rows.

### Path B: `public.atpx__nmea_*` — parsed NMEA 0183 sentences

Fed by `zero-atpx-nmea` (see `asyncapi.json`), routed 1 table per sentence
type by `vector/processing/atpx_nmea_route.vrl` (`atpx__nmea_<type>`).
Confirmed tables that actually exist right now: `alc, alr, dbt, dpt, fec,
gga, gll, hdt, mxs, pos, rmc, rot, vbw, vhw, vlw, vtg, zda`. **No `mwv`
(wind) or `rsa` (rudder) table exists** — confirms A+T isn't sending those
as NMEA sentences on this boat; wind/rudder/heel/leeway only come through
Path A. `mxs` is an undocumented type (not in `asyncapi.json`'s curated
list) — unclear what it carries.

Useful as a cross-check / fallback for BSP specifically:
`atpx__nmea_vhw.water_speed_knots` (speed through water, log-derived) or
`atpx__nmea_vbw.lon_water_spd` (Doppler log). Otherwise, **use Path A for
everything on this dashboard** — it's simpler (one table, named fields) and
already covers every requested datapoint.

---

## 3. Reference performance curves

Source: `Hydro generator yield issue A 20240430.pdf` (Dykstra Naval
Architects, project 19-21, issue A, 2024-04-30). No live-data dependency.

Gives, per pod:
- **AFT prop**: Ø1.5 m, base drag 0.111 m². **FWD prop**: Ø1.2 m, base drag
  0.070 m².
- 4 discrete pitch settings (**CP1–CP4**) per pod, each with `P0.7/D`, `cp`
  (power coefficient), `η` (efficiency).
- **POWER [kW] vs Vs [kts]** table, 6–18 kts in 1-kt steps, for each of
  CP1–CP4, separately for AFT and FWD.
- **Associated drag [kN] vs Vs [kts]** table (BASE + CP1–CP4), separately
  for AFT and FWD.

No closed-form formula is printed on the page — these are pre-computed
tabulated outputs. Plan: embed the ~48 points/pod as a static lookup
(interpolated between the 1-kt steps) for the scatter-plot reference curves,
rather than re-deriving the underlying propeller theory. You mentioned a
more detailed Excel version exists — worth using instead if the extra
resolution/pitch settings matter, but the PDF is enough to start.

---

## 4. Open questions — take these to the PCS/Marpower engineer

1. **`propellor_sailing_mode__value` (0–4) → label mapping** (Gen / Prop /
   Man / Motorsail / Free). Couldn't infer this from data — the helm-station
   "mode selected" feedback flags never went true in the last 30 days of
   data checked. Need either documentation, or to watch the value live while
   someone cycles through modes.
2. **`speed_or_torque_setpoint__value` (Aradex, per drive) is BOOLEAN, not a
   magnitude** — you mentioned you're already requesting this change; noting
   it here so it's tracked. Until fixed, the dashboard can only show a
   torque-mode/speed-mode flag, not an actual setpoint trace.
3. **`motor_power_in_perc__value` units** — it's a percentage of something.
   What's the rated/nominal power per pod, to convert to kW? Or should this
   just be displayed as a percentage?
4. **`output_velocity__value`** — please confirm this is genuinely propeller
   shaft RPM (as opposed to a motor-side or gearbox-side reading). If so,
   what's its relationship to `speed_setpoint__value` /
   `reference_frequency__value` (which is the actual commanded value, and
   which is a normalized/derived signal)?
5. **"Total power" / "Total torque"** at the top PCS-general level — is
   fwd + aft (of whichever source we pick as canonical) the right
   definition, or is there an authoritative combined value we should use
   instead? (See §1 — we're currently planning to *not* trust
   `marpower__150000_propulsion`/`_general` for this, since their schemas
   look like unrelated catch-alls.)
6. **Hydrogen efficiency formula** — what's the actual definition? (e.g.
   measured electrical power ÷ theoretical power from the reference curve at
   current boat speed + pitch? Something else?) What inputs beyond
   power/BSP/pitch does it need?
7. **Are the `marpower__150000_propulsion` (bare) and `_general` tables
   meaningful sources of anything**, or safe to ignore entirely for this
   dashboard? Their column sets look like a mixed union of PCS + Aradex +
   helm fields with no pod identifier, and a separate set of
   fwd/aft/bow/stern thruster winding/bearing temps that may belong to a
   different (non-hydrogeneration) thruster-health-monitoring topic
   entirely.
8. **`atprocessor_0` as the canonical A+T sender** (§2) — please confirm
   this is the primary/certified feed for wind, heel, rudder, leeway and
   BSP on this boat, not one of several redundant paths we should instead
   pick per-field.
9. **`speed_or_torque_setpoint__value` polarity** — which boolean value
   (`true`/`false`) means "torque mode" vs "speed/RPM mode"? Only `false`/
   `null` observed live so far, so this can't be inferred from data either.
   (Related to #2 — once this becomes a real setpoint value the polarity
   question may become moot.)

---

## 5. Explicitly out of scope for v1

- Lever setting (you said to leave it out, even though the data exists in
  `pcs_{fwd,aft}_pshelm/sbhelm`).
- Anything from the commissioning test-PLC rig (`prop_test__data` /
  `devices__can_aradex.*`) — not available going forward.

---

## 6. Handoff — implementation status (as of 2026-09-22)

The dashboard itself now exists and is **live and rendering correctly** at
`zero-dashboards/dashboards/Commissioning/hydrogeneration-dashboard.json`
(confirmed by hand in Grafana at `grafana.sy-zero.com`, not just query-tested).
Layout/panel-arrangement feedback from you is still pending ("I'll get back
to layout") — everything below is about data correctness and Grafana/
GreptimeDB plumbing, not the visual arrangement.

### What's built

- **General row**: PCS overview table (fwd/aft latest snapshot), A+T overview
  table (BSP/AWA/AWS/heel/leeway/rudder latest snapshot), total power/torque
  stat panels (computed fwd+aft, not from the untrusted catch-all tables),
  two trend timeseries.
- **Per-pod performance detail** (one collapsible row, two columns — FWD at
  `x=0`, AFT at `x=12`, matching `y` per panel-type so rows line up): status
  table, sailing-mode-over-time status-history, torque/power/RPM comparison
  timeseries (all sources overlaid, setpoint as a stepped line where a
  numeric setpoint exists), hydrogen-efficiency placeholder text panel.
- **Performance curves**: one XY chart per pod — 4 static reference lines
  (CP1–CP4, grey shades, from the PDF), live bucketed points (colour =
  continuous pitch), and a separately-queried "current" point (fixed larger
  square marker) using a trailing rolling window rather than the historical
  bucket grid.

The dashboard JSON was built with a **throwaway Python generator script**
(lived in the session scratchpad, never committed). There is no generator
in the repo — if you need to regenerate or bulk-edit panels programmatically
in a future session, either hand-edit the JSON directly (it's plain Grafana
dashboard JSON, schemaVersion 42) or write a fresh generator; don't go
looking for the old one.

### Gotchas discovered while building this — read before editing panels/queries

1. **GreptimeDB SQL: `UNION ALL` branches with their own `ORDER BY … LIMIT`
   must each be parenthesized individually**, e.g.
   `(SELECT … ORDER BY timestamp DESC LIMIT 1) UNION ALL (SELECT … ORDER BY
   timestamp DESC LIMIT 1)`. Without the parens you get a parser error at the
   `UNION` keyword. Doesn't apply to branches without their own ORDER
   BY/LIMIT.
2. **The Greptime Grafana datasource's `$__timeFilter(...)` macro breaks on
   qualified column names.** `$__timeFilter(t.timestamp)` gets turned into a
   filter on a column *literally named* `"t.timestamp"` (dot included in the
   name) instead of `t."timestamp"`, and Greptime rejects it ("No field named
   \"t.timestamp\""). Fix: always apply `$__timeFilter(...)` to the bare
   `timestamp` column inside each branch/subquery *before* it gets aliased,
   never on a dotted reference to an outer alias.
3. **Short-form interval literals work fine** in this GreptimeDB version —
   confirmed both `date_bin('5m', ts, …)` and `now() - INTERVAL '5m'` parse
   correctly, no need to spell out `'5 minutes'`.
4. **Grafana's XY Chart panel (`type: "xychart"`) schema — verified against
   `grafana/grafana`'s actual source, not memory, after getting it wrong
   twice:**
   - Top-level option key is **`mapping`** (`"auto"` or `"manual"`), not
     `seriesMapping`.
   - Per-series `x`, `y`, `color`, `size` are all `{"matcher": {"id": ...,
     "options": ...}}` — a field matcher, not a raw field name or a
     `{fixed: ...}` shorthand.
   - **`frame` matching only supports `{"id": "byIndex", "options": N}`** in
     the actual shipped runtime (`utils.ts`'s `getFrameMatcher2` — there's a
     literal `// cause we dont have a proper matcher for this currently`
     comment in Grafana's own source). `N` is the query's 0-based position
     among the panel's `targets`, in target order. Any other matcher id
     (`byRefId`, `byFrameRefID`, etc.) silently matches **zero** frames →
     empty series list → the panel renders a plain grey **"Err"** box with no
     stack trace, no console error, nothing to debug from — it looks
     identical to a dozen other possible failures. If you see that, suspect
     this first.
   - Points-vs-lines style, point size/shape/stroke width are **not**
     series-level options — they're `fieldConfig.custom.show` /
     `custom.pointSize{fixed,min,max}` / `custom.pointShape` /
     `custom.pointStrokeWidth`, set via per-frame field overrides (using
     `byFrameRefID` — a *field* matcher, correct here, unlike in `frame`
     above — confusingly the two matcher-id namespaces overlap in name but
     aren't interchangeable).
5. **Status-history / categorical-over-time panels**: don't `GROUP BY
   date_bin(...)` a slow-changing categorical column — at fine granularity
   this blows past Grafana's point-count warning fast. Instead query only
   the **transitions**: `LAG(value) OVER (ORDER BY timestamp)` and keep a row
   only where `prev IS NULL OR prev <> value`. Verified: a 10-minute stable
   window went from ~200 rows to 1. Note this can still return a lot of rows
   if the underlying signal is genuinely flapping (observed: 94.5k
   transitions for `propellor_sailing_mode__value` over 30 days on `pcs_fwd`
   — real rapid oscillation, not a query bug; worth mentioning to the PCS
   engineer alongside open question #1, since it smells like noise near a
   threshold rather than deliberate mode changes).
6. **Scatter "current point" should be its own query**, using a trailing
   window (`timestamp > now() - INTERVAL '$var'`) rather than picking out the
   last row of the historical bucket grid — avoids a partial/stale last
   bucket, and lets the current point be a visually distinct series (fixed
   size/shape) independent of how the historical points are styled.
7. **Status-history bar colors can look wrong even when the mapping config is
   correct.** With the transitions-only query (gotcha #5) feeding very
   sparse, unevenly-spaced points (e.g. a short blip next to multi-day-long
   stable stretches), some bars rendered the wrong color visually — but the
   **legend** (which uses the exact same `field.display(value).color` code
   path as the bars, per `TimelineChart.tsx`) showed the correct color for
   every mapped value, confirming the value-mapping config itself is fine.
   Read through Grafana's actual rendering source
   (`app/core/components/TimelineChart/*`) and didn't find an index/position-
   based fallback that would explain it — most likely
   `prepareTimelineFields`'s gap-null-insertion heuristic getting confused by
   the extreme unevenness between a narrow blip and long stable gaps. Not
   worth chasing further while mode labels/colors are still placeholder
   (open question #1) — revisit if it persists once real labels are in.

### Still open

- Every item in §4 (open questions) is still unanswered.
- Layout/arrangement review with you hasn't happened yet.
- Hydrogen efficiency panel is a placeholder only (§4 Q6).
- Reference curves use only the coarse PDF table; the more detailed Excel
  version (mentioned but not yet supplied) could replace it later.


## Notes from user 

Variables to figure out the meaning of or add to dashboard: 
- Add loadpins per thruster? 
- Add azimuth per thruster
- motor_ prefix keys? frequency, power, thermal state, etc 
- separate aradex block needed? 
- batteries power?
- pitch pos? 
- reference frequency? 
- output velocity?
- action_level? 

Review aradex topics... 

