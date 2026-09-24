# Hydrogeneration & propulsion dashboard — plan

## 0. Project

A sea-trial Grafana dashboard for the two azimuthing pods (FWD, AFT),
covering hydrogeneration performance, propulsion performance, and enough
supporting telemetry to sanity-check both. It runs against live production
data in GreptimeDB (`greptime-zero.tail0b4840.ts.net:4000`), not the
commissioning test-PLC rig.

A first version is live at `hydrogeneration-dashboard.json`, built against
the old data layout. **This document is the plan for the rebuild.**

**Nothing here can be implemented yet.** It is blocked on a chain: Marpower
deploys the revised Modbus map → the new signals appear on MQTT → the Vector
ingest is restructured (§2.3) → panels can be built. This document exists so
that all of it is lined up and agreed before that chain completes.

---

## 1. Current state

### 1.1 The PCS Modbus list

`52422003 Modbus RTU interface PMS PCS R1.6` (changes highlighted yellow).
Two tabs, **FWD only**: `From PCS to PMS (fwd)` (registers 0–83) and
`From PMS to PCS (Fwd)` (registers 100–101).

What R1.6 settles:

- **Sailing mode** (reg 45): `0=Off, 1=Sailing, 2=Prop, 3=Manou, 4=HydroGen`.
- **Aradex power** (regs 35/40): DC power in **kW, ×10 scaling** — computed
  from DC volts × amps. Per drive; the two drives sum to pod electrical
  power.
- **Registers 64–83 are a Schneider Altivar drive** — the hydraulic power
  pack pump, *not* the propulsion motor. The propulsion train is Aradex
  (regs 32–42). Everything named `motor_*` in the current PCS table belongs
  to this pump drive.
- **Withdrawn registers**: 54 (`action_level`, *"Is vervallen"*), 46.6/46.7
  (brake control, *"removed from PCS"*), 10 and 11 (*"I/O NA"*).
- **Battery fields** are on the PMS→PCS tab with no register assigned — they
  are values we send *to* the PCS, not PCS telemetry.

What R1.6 does **not** contain: any torque setpoint, any speed-vs-torque mode
indicator, the AFT register map, and the propulsion-motor protection IO
(winding/bearing/vent temps, water leak, com alarm) that nonetheless arrives
in GreptimeDB today.

### 1.2 Current GreptimeDB tables

Live under `marpower__150000_propulsion__*`:

| Table | Measures | Contents |
|---|---|---|
| `pcs_fwd`, `pcs_aft` | 111 / 110 | Everything not on a sub-topic: PLC I/O, alarms, pitch/azimuth/mode, shear beams, load pins, the Schneider block, motor protection |
| `pcs_{fwd,aft}_ara1`, `_ara2` | 25 each | Per-drive Aradex telemetry |
| `pcs_{fwd,aft}_pshelm`, `_sbhelm` | 25 each | Helm stations |

Row shape: every `<measure>__value` / `__is_valid` / `__has_value` /
`__timestamp` clump is populated on **every** row — dense per-scan-cycle
snapshots, so `ORDER BY timestamp DESC LIMIT 1` gives a complete snapshot
with no forward-fill needed.

Ignore `marpower__150000_propulsion` (bare), `_general`, `_ara`,
`marpower__150000propulsion__*` (no underscore) and `*_old` — legacy
catch-alls with mixed, pod-ambiguous schemas.

Known data problems in the current tables:

- **`shear_beam_calculated` reads 0** while raw `shear_beam_1..4` read
  ~−1200, with `is_valid = true`. Unusable as a torque source.
- **Duplicate columns** for one signal: `24_vdcservfail` / `24_vdcemergfail`
  alongside `pcscb_11_service_24_vdc_failure` /
  `pcscb_11_emergency_24_vdc_failure`.
- **`pcs_fwd` carries both `emergency_control_fwd` and
  `emergency_control_aft`**; R1.6 defines one per PCS.
- **Naming drift between pods**: `winding_temp_w_1` (fwd) vs
  `windingtempw_1` (aft) — any symmetric query silently misses a pod.
  Also `pitch_pos_sesnor_failure` (sic).
- **KEB numbering mismatch**: R1.6 has KEB12 = Helm PS, KEB13 = Helm SB; we
  ingest `keb_13_*` and `keb_14_*`.
- **The four helm tables are 2 stations × 2 relaying PCSs.** Schemas are
  identical and each carries both `fwd_thruster_*` and `aft_thruster_*`
  columns. Both PCSs read the same physical helm bus, so the fwd/aft
  distinction is provenance, not data (sampled at one instant:
  `pcs_fwd_pshelm` 16412, `pcs_aft_pshelm` 16304 for the same lever).
- `zero-data/snapshot/` holds one stale table (80 measures vs 111 live).

### 1.3 Feedback on R1.6 — errors to report

1. Reg 45 enum reads `33=Manou`; should be `3`.
2. Reg 46 bit 9 assigned **twice**: "Hydraulic Pump Frequency Drive Ready"
   and "PSHelmStationSelect".
3. PMS→PCS tab: **three signals share register 101** —
   `FwdAra1MaxPowerSetpointGenerator`, `FwdAra2MaxPowerSetpointMotor`,
   `FwdAra2MaxPowerSetpointGenerator`. Only `FwdAra1MaxPowerSetpointMotor`
   (100) is unique.
4. Reg 0 bit 11 has a blank signal name.
5. "Hydraulic Pump Motor Temperature" listed as `analog` with no register.
6. `…MaxPowerSetpointGenerator` described as "minimum allowed power to
   consume" — sign convention needs stating (generating = negative?).
7. `motor_run_time` (80) and `power_on_time` (82) are Unsigned32 "dubbel
   register" — confirm decode across 80–81 / 82–83.

---

## 2. Field mapping & ingest

### 2.1 A+T instrument data

Use **`public.atpx_raw`**, A+T's raw instrument bus, landed by Vector as one
long/EAV table: `atpx_raw(timestamp, topic, sender, field, value)`. Field-id
and sender dictionaries are in `vector/processing/atpx_0_consts.vrl`.

Filter **`sender = 'atprocessor_0'`** uniformly — A+T's own fused output,
and the only sender that publishes every field we need.

| Datapoint | `field` |
|---|---|
| BSP | `boat_speed_kts` |
| AWA / AWS | `app_wind_angle` / `app_wind_speed_kts` |
| TWA / TWS | `true_wind_angle` / `true_wind_speed_kts` |
| Heel | `heel_angle_deg` |
| Rudder | `rudder_angle_deg` |
| Leeway | `signed_leeway` |

**`atpx_raw` is high-volume** — always filter tightly on time *and*
`field`/`sender`. The dashboard's time picker does this via `$__timeFilter`;
ad-hoc queries need care, and the scatter plots must bucket before joining,
never join raw rows.

### 2.2 PCS fields

| Datapoint | Source | Column |
|---|---|---|
| Sailing mode | PLC | `propellor_sailing_mode` (0–4, §1.1) |
| Pitch / azimuth | PLC | `propellor_pitch`, `propellor_azimuth` |
| Prop shaft RPM | PLC | `propeller_speed` — reg 55, **÷10 → rpm**, not yet ingested |
| Torque, per drive | Aradex | `torque` (×2 drives per pod) |
| Torque, shear beam | Loads | `shear_beam_1..4` (`shear_beam_calculated` is broken) |
| Power, per drive | Aradex | `power` — **÷10 → kW** |
| **Pod electrical power** | Aradex | `ara1.power/10 + ara2.power/10` |
| Drive RPM | Aradex | `speed` |
| Power limits | Aradex | `max_power_setpoint_motor`, `max_power_setpoint_generator` |
| Power limited? | PLC | `aradex1/2_power_limited` — reg 2.9/2.10, not yet ingested |
| Hydrogen over/underspeed | PLC | reg 3.4/3.5, not yet ingested |
| Setpoint-not-reached | PLC | `pitch_`, `rpm_`, `azimuth_setpoint_not_reached` |
| Load pins | Loads | `loadpin_1..4_{horizontal,vertical}` |
| Helm levers & mode | Helm | `{ps,sb}_*_thruster_lever_*`, `*_mode_select{,ed}_*` |
| Hydraulic pump drive | Schneider | `motor_*`, `output_velocity`, `speed_setpoint`, `reference_frequency`, `drive_thermal_state`, … |

**Total power / total torque** = FWD + AFT of the chosen source, computed by
us. Do not use the legacy catch-all tables.

### 2.3 Proposed topic structure & Greptime tables

Vector routes **topic → table, one-to-one**
(`vector/processing/process_2_table.vrl`: a dict keyed on topic, else the
table name is derived from the topic with `/`→`__`, `-`→`_`). There is no
field-level routing. So the split has to happen **upstream, in the MQTT topic
structure** — which is exactly how the Aradex and helm splits already work,
and requires **zero Vector changes**.

Proposed topics (we are free to choose these):

```
marpower/150000-propulsion/pcs-{fwd,aft}-plc
marpower/150000-propulsion/pcs-{fwd,aft}-ara1
marpower/150000-propulsion/pcs-{fwd,aft}-ara2
marpower/150000-propulsion/pcs-{fwd,aft}-schneider
marpower/150000-propulsion/pcs-{fwd,aft}-loads
marpower/150000-propulsion/pcs-{fwd,aft}-motor
marpower/150000-propulsion/pcs-{fwd,aft}-helm
```

Resulting GreptimeDB tables — **14**, all named automatically by the existing
fallback rule:

| Table (× `fwd`, `aft`) | ~Measures | Contents |
|---|---|---|
| `…__pcs_{pod}_plc` | ~60 | Pitch, azimuth, sailing mode, propeller speed; alarm registers 0–3; hydraulic valve/pump I/O; setpoint-not-reached flags |
| `…__pcs_{pod}_ara1` / `_ara2` | 25 each | Aradex drive telemetry, error/warning bit decodes, power setpoints |
| `…__pcs_{pod}_schneider` | 18 | Hydraulic pump VFD, registers 64–83 |
| `…__pcs_{pod}_loads` | 13 | `shear_beam_1..4`, `shear_beam_calculated`, `loadpin_1..4_{h,v}` |
| `…__pcs_{pod}_motor` | 13 | Propulsion-motor protection: bearing DE/NDE, winding U/V/W ×2, vent ×2, heating, com alarm, water leak |
| `…__pcs_{pod}_helm` | ~50 | **Both stations in one topic**, fields prefixed `ps_` / `sb_` |

Notes on the choices:

- **`motor` is an addition to the list discussed.** The propulsion-motor
  protection IO is not PLC and not Schneider, it is a distinct device, and we
  do not currently know which interface publishes it (§2.4). Giving it its
  own topic keeps that question isolated.
- **Helm carries both PS and SB** in one message, per preference. This takes
  4 helm tables → 2. The remaining fwd/aft duplication is inherent — both
  PCSs relay the same helm bus — so **queries must pick one pod's copy as
  canonical** rather than unioning. Worth a comment in the panel SQL.
- Helm messages keep their existing `fwd_thruster_*` / `aft_thruster_*`
  field split *inside* each station, so a full column is e.g.
  `ps_fwd_thruster_lever_speed_signal`.
- This drops `pcs_fwd` / `pcs_aft` as tables entirely; `-plc` replaces them.

Cleanups to fold into the same migration: drop the withdrawn registers
(§1.1), the duplicate 24 V pair, the stray `emergency_control_aft` in the FWD
table; normalise `winding_temp_w_1` / `windingtempw_1`; fix
`pitch_pos_sesnor_failure` (`process_5_spell_fix.vrl` already exists for
this); settle KEB12/13/14; refresh `zero-data/snapshot/`.

### 2.4 Open points

**Signals that do not exist and must be requested:**

1. **Torque setpoint per Aradex drive** — the active commanded value. R1.6
   lists "Speed or Torque Setpoint Signal (Aradex1/2)" as CAN with no
   register assigned.
2. **Max torque per Aradex drive** — "Max Torque Signal (Aradex1/2)", same.
3. **Speed-vs-torque control-mode indicator** — absent in any form. Needed
   to interpret 1 and 2 at all.
4. **Rated / nominal power per pod** — a constant, to sanity-check the
   Aradex kW sum.
5. **Load-pin and shear-beam units and scale factors** — R1.6 gives
   registers but no scaling.
6. **Propulsion reference curves** (§3.2).

**In R1.6 but not yet published to MQTT:**

7. `PropellerSpeed` (reg 55, ×10) — the only true prop shaft RPM.
8. `HydroGenUnderSpeed` (3.4), `HydroGenOverSpeed` (3.5).
9. `Aradex1/2 PowerLimited` (2.9 / 2.10).
10. `KEB13_PowerModule2FuseBlown` / `…PowerFailure` (3.8 / 3.9).
11. `EXOR_HMI_SB/PS_CommError` (2.2 / 2.3).
12. `PCS 2 Ground Fault Diagnostics Enabled` (2.8).

**Questions:**

13. Confirm registers 64–83 ("Schneider Drive") are the **hydraulic pump
    VFD**, not the propulsion motor.
14. Which interface publishes the **propulsion-motor protection IO**
    (bearing/winding/vent temps, `waterleakalarm`, `comalarm`,
    `heatingonoff`)? It is in GreptimeDB but nowhere in R1.6.
15. **AFT register map** — R1.6 is FWD-only. Send the AFT tab, or the offset
    rule. It is not a pure copy: reg 1.14/1.15 notes *"AFT ==KEB10
    FWD ==KEB11"*.
16. `shear_beam_calculated` (reg 13) reads **0** while raw beams read ~−1200.
    Broken calculation, or did the register move?
17. KEB numbering: R1.6 says KEB12 = Helm PS, KEB13 = Helm SB; we ingest
    `keb_13_*` / `keb_14_*`. Which is right?
18. Confirm regs 10, 11, 54, 46.6, 46.7 are genuinely withdrawn so the
    columns can be dropped.
19. Sailing mode flaps ~94.5k times in 30 days, and `HydroGen` (4) appeared
    only ~16 times. Deliberate, or noise near a threshold?
20. **Hydrogen efficiency formula** — what is the actual definition?
    (Measured electrical power ÷ theoretical power from the reference curve
    at current BSP and pitch? Something else?) What inputs does it need
    beyond power / BSP / pitch?
21. Is `atprocessor_0` the primary/certified A+T feed for wind, heel, rudder,
    leeway and BSP on this boat?

---

## 3. Reference curves

### 3.1 Hydrogeneration — have

Source: `Hydro generator yield issue A 20240430.pdf` (Dykstra Naval
Architects, project 19-21, issue A, 2024-04-30). No live-data dependency.

Per pod — **AFT** Ø1.5 m, base drag 0.111 m²; **FWD** Ø1.2 m, base drag
0.070 m² — it gives 4 discrete pitch settings (**CP1–CP4**) each with
`P0.7/D`, `cp`, `η`, plus two tabulated curves over Vs = 6–18 kts in 1-kt
steps: **POWER [kW] vs Vs** and **associated drag [kN] vs Vs** (BASE +
CP1–CP4).

No closed-form formula is printed — these are pre-computed outputs. Plan:
embed the ~48 points per pod as a static lookup, interpolated between the
1-kt steps. A more detailed Excel version was mentioned but not supplied; it
could replace the PDF table later if the extra resolution matters.

### 3.2 Propulsion — needed

The propulsion scatter plot (§4.2) needs the equivalent reference set, which
we do not have. To be supplied:

- **Power [kW] vs Vs [kts]**, per pod, per pitch setting — the propulsion
  counterpart of the hydrogeneration table.
- The **pitch settings** the curves are defined at (are they the same CP1–CP4
  points, or a different set for propulsion?).
- **Thrust [kN] vs Vs**, if available — the counterpart of the drag table.
- Whether the curves are per pod or for both pods combined.
- Design/rated operating point, for a reference marker on the plot.

Same treatment as §3.1: static embedded lookup, interpolated.

---

## 4. Dashboard plan

### 4.1 Rows

**General.** PCS overview table (FWD/AFT latest snapshot), A+T overview table
(BSP / AWA / AWS / heel / leeway / rudder), total power and total torque
stats (computed FWD + AFT), two trend timeseries.

**Per-pod performance detail** — one collapsible row, two columns (FWD at
`x=0`, AFT at `x=12`, matching `y` per panel type so the rows line up):
status table, sailing-mode status-history, torque / power / RPM comparison
timeseries, hydrogen efficiency (pending §2.4 Q20).

Torque and power series are Aradex-only plus raw shear beams. **No Schneider
signals on any performance panel**, and no setpoint trace until a real
setpoint exists.

**Hydrogeneration performance curves** — one XY chart per pod: 4 static
reference lines (CP1–CP4, grey), live bucketed points coloured by continuous
pitch, and a separately-queried "current" point as a larger fixed marker.

**Propulsion performance curves** *(new)* — mirror of the above, one XY chart
per pod, same construction, using the §3.2 curves once supplied. Power on Y,
BSP on X, points coloured by pitch. Filter to `propellor_sailing_mode = 2`
(Prop) so propulsion and hydrogeneration points don't contaminate each
other's plots; the hydrogeneration charts filter to mode `4` likewise.

**Pod loads** *(new)* — two columns, per pod:

- **Load-pin XY scatter**, horizontal vs vertical, one series per pin —
  shows load *direction and magnitude* per pin at a glance, which a
  timeseries cannot. Current value as a larger marker, recent history faded.
- **Load-pin timeseries**, 8 series (4 pins × H/V): H and V by line style,
  pin number by colour.
- **Latest-snapshot table**: pin, horizontal, vertical, alongside the 4 raw
  shear beams, so both load measurements sit together.

Confirmed live and varying on both pods: over 2 h on `pcs_fwd`,
`loadpin_1_horizontal` −1117…−1018, `loadpin_1_vertical` peaking 2224,
`is_valid` true. Axes labelled "raw" until units are supplied (§2.4 Q5).

**Drive limits & control** *(new)* — no graphs, tables only:

- **Aradex power limits**, per pod per drive: `max_power_setpoint_motor`,
  `max_power_setpoint_generator`, actual `power`, and the
  `aradex1/2_power_limited` flag — so a power ceiling on the scatter plots
  can be explained immediately.
- **Helm station control**, sanity check: which station is selected
  (`station_selected`), the per-pod mode select and selected flags, and lever
  positions. Table only. Remember only one pod's copy of the helm data is
  canonical (§2.3).

**Hydraulic & Schneider health** *(new)* — a single table, no graphs. These
units are not important to performance, but we are currently seeing
implausible values (e.g. 150 Nm torque) and want them visible enough to
notice drift: `output_velocity`, `motor_frequency`, `motor_torque`,
`motor_current`, `motor_voltage`, `motor_power_in_perc`, `mains_voltage`,
`drive_thermal_state`, `motor_thermal_state`, `device_state`,
`motor_run_time`, `power_on_time`, plus `hydr_system_press` and the pump
frequency-drive enable/ready/fault-code from the PLC table.

### 4.2 Implementation notes

The dashboard JSON was built with a throwaway Python generator that was never
committed. Hand-edit the JSON (plain Grafana, schemaVersion 42) or write a
fresh generator; there is nothing in the repo to reuse.

Hard-won specifics, all verified against Grafana source rather than memory:

- **GreptimeDB SQL**: `UNION ALL` branches that carry their own `ORDER BY …
  LIMIT` must each be **individually parenthesized**, or the parser fails at
  `UNION`. Short-form interval literals (`'5m'`) work fine.
- **`$__timeFilter(...)` breaks on qualified column names** —
  `$__timeFilter(t.timestamp)` filters a column literally named
  `"t.timestamp"`. Always apply it to the bare `timestamp` column inside each
  subquery, before aliasing.
- **XY chart (`type: "xychart"`)**: top-level option key is **`mapping`**
  (not `seriesMapping`). Per-series `x`/`y`/`color`/`size` are field matchers
  (`{"matcher": {"id": …, "options": …}}`). **`frame` matching only supports
  `{"id": "byIndex", "options": N}`** where N is the target's 0-based
  position — any other matcher id silently matches zero frames and the panel
  renders a bare grey **"Err"** box with nothing to debug from. Point
  style/size/shape live in `fieldConfig.custom` (`show`, `pointSize`,
  `pointShape`, `pointStrokeWidth`) via per-frame overrides using
  `byFrameRefID` — a *field* matcher, confusingly sharing a name-space with
  the `frame` matchers above but not interchangeable.
- **Status-history panels**: never `GROUP BY date_bin(...)` a slow-changing
  categorical — query the **transitions** instead (`LAG(value) OVER (ORDER BY
  timestamp)`, keep rows where `prev IS NULL OR prev <> value`). A 10-minute
  stable window drops from ~200 rows to 1. With very sparse, unevenly-spaced
  points some bars can still render a visually wrong colour while the legend
  is correct — most likely `prepareTimelineFields`' gap-null heuristic.
  Revisit once real mode labels are in.
- **Scatter "current point" is its own query**, using a trailing window
  (`timestamp > now() - INTERVAL '$var'`) rather than the last row of the
  historical bucket grid — avoids a partial last bucket and lets it be styled
  independently.

### 4.3 Out of scope

Anything from the commissioning test-PLC rig (`prop_test__data`,
`devices__can_aradex.*`) — not available going forward.
