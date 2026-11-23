# Energy dashboards: completeness of the consumer side

Analysis of 11 Nov 2026, on greptime-zero data from 4–11 Nov 2026 (Zero at the dock on shore power),
after [PR #996](https://github.com/foundation-zero/zero/pull/996) added shore power to dbt and the two energy dashboards.

**Question:** which data points are still missing from the energy dashboards and the dbt models, and can
they be placed in the existing consumer main groups (Domestic, HVAC, Technical, Propulsion) and sub groups?

## Summary

- About **690 kWh/day** reaches the 700 VDC bus (shore minus battery charging; no solar that week). The
  dashboards show about **322 kWh/day** of consumption, of which **74 kWh/day is counted twice**.
- Measured but not on the dashboards: 24 VDC system output (≈ 66 kWh/day), 350 VDC lighting (≈ 67 kWh/day),
  shore converter losses (≈ 84 kWh/day), grid converter losses (≈ 29 kWh/day), AC load without power tags
  (≈ 72 kWh/day).
- Truly unmeasured: **≈ 140 kWh/day** of 700 VDC consumers (winches, power packs, heaters, chiller, pumps,
  drive standby). Individual consumers have no power signal, but the DC ring switches let us measure it
  **per bus segment**.
- Almost everything fits the four main groups with new sub groups. Conversion losses don't: they need a
  fifth group, **Losses**.
- Two bugs: the double counting above, and the Aradex views fail on greptime-zero, so Propulsion and
  Hydrogeneration are empty there.

## How the analysis was done

1. **Electrical layout** from the yard documents (zero-docs-mcp):
   - *9445203-2 Functional description Project Zero v5.0*, pages 11–15: what is connected to each 700 VDC
     panel (+SB.01.P01–P04, +SB.02.P01–P02) and to the sub-distributions DB-HDC02–06.
   - *9445203-1 Functional description Project Zero v3.0*, page 12: voltage levels (700 VDC, 350 VDC,
     400 VAC, 24 VDC) and what they feed.
   - *9445209-3 Functional Description AMCS R2.5*, pages 132–140: producers and consumers on the 700 VDC
     ring, and the 350 VDC system.
   - *9445419 AC DB fwd corridor 10P3*, pages 5–9: the groups behind sub-board 10P3.
   - *9445231 Mus manual*, page 26: section 0 is the left side of a DC ring switch.
2. **What is modelled now:** the dbt models in `dbt/models`, the metadata in
   `dbt/macros/load_power_tag_metadata.sql` and `load_24vdc_metadata.sql`, and the queries in the two
   dashboards under `zero-dashboards/dashboards/Energy`.
3. **What is measured:** the raw tables on greptime-zero, and the Marpower IO list
   `io_lists/io-list ~ help ~ totals.xlsx` (17,322 rows, including the PMS devices KEB1–KEB9), searched for
   every power, current and energy signal.
4. **How much:** 7-day averages per signal, and for the ring balance 7 days of 1-minute data analysed in
   Python (least-squares fits per bus segment).

**Limits of the numbers:**

- Many signals are published only when they change, so plain averages are skewed. Treat the numbers as
  ±10–20 %.
- Units (W or kW) were inferred from the size of the values and cross-checked where possible.
- Per bus segment the error is about ±1 kW (see finding F7).

## Findings

### F1. Feeders of 10P1 and 10P2 are counted twice (bug)

- **What:** power tags `power-tags/10P0-1/power-distr-panel-aft-10p1` (PT135Q01) and
  `power-tags/10P0-3/power-distr-panel-galley-10p2` (PT335Q01) measure the feeders of sub-boards 10P1 and
  10P2. Both are classified Technical/Technical. Every consumer on 10P1 and 10P2 has its own tag as well.
- **Meaning:** the same energy is counted twice. Technical is about 74 kWh/day too high (≈ 23 % of all
  consumption shown).
- **How found:** 7-day totals per panel from `gld_power_tags_power_per_minute_per_sub_group`. Feeder 10P1
  41.0 kWh/day against 40.0 for its consumers combined. Feeder 10P2 32.8 against 31.8.
- **Note:** the 10P3 feeder (≈ 40 kWh/day) is *not* a double count, because the consumers behind 10P3 have
  no tags (F6).

### F2. Aradex views fail on greptime-zero (bug)

- **What:** querying `views.gld_aradex_power_per_minute_per_main_group` (and `slv_pcs_aradexes`) on
  greptime-zero fails with
  `Field 'power__value' in Substrait schema has a different type (Int64) than the corresponding field in the table schema (Float64)`.
- **Meaning:** on Zero, the Propulsion and Hydrogeneration series on both dashboards are empty. The view was
  compiled while `power__value` was an integer; the column is now a float.
- **How found:** the error came back on the first query over the gold views.

### F3. Shore converter losses ≈ 3.5 kW (84 kWh/day)

- **What:** the ESI reports both its AC input (`esi_ac_bus_active_power_3_phase__value`, kW) and its DC-side
  current (`esi_battery_current__value`, A). Converter 07-11 takes 14.9 kW AC and delivers 12.9 kW DC.
  Converter 07-12 takes 18.0 kW AC and delivers 16.5 kW DC (DC current × ≈ 660 V bus voltage).
- **Meaning:** PR #996 books the AC power as "Shore" production. About 11 % of that never reaches the bus.
  Unless the difference is booked as a loss, production and consumption can't balance.
- **How found:** 7-day averages per ESI module. The ring balance (F7) confirms it: with the AC values, the
  segments holding the ESI showed 3.3–3.5 kW of unexplained load; with the DC values, 1.4–2.0 kW.

### F4. 24 VDC system: most of the load is not behind monitored breakers

- **What:** the 24 VDC converters (`marpower__450000_24vdc_system`, topics `conv/w14e*`) deliver about
  2.8 kW, or 66 kWh/day. The breaker-level model (`gld_24vdc_power_per_minute_*`) accounts for about
  2.6 kWh/day.
- **Meaning:** about 64 kWh/day of 24 VDC load (PLCs, AMCS, network, KVM and so on) is missing from the
  dashboards.
- **How found:** converter `power__value` (W) against the breaker-level gold view.

### F5. 350 VDC lighting is not on the dashboards

- **What:** the four Epic Power 350 V converters (`marpower__450000_dc_distribution__350v_conv_aft_1/2`,
  `fwd_1/2`, column `hvdc_power__value`, W) draw about 2.8 kW, or 67 kWh/day. According to the functional
  description, the 350 VDC network feeds the accommodation lighting.
- **Meaning:** a measured hotel load that the dashboards don't show.
- **Also:** the per-output measurements (`marpower__450000_350vdc_system`, DcOpp1/2 modules U101/U102/U104,
  line power in kW) stopped publishing on 27 Oct. With them, the 350 VDC load could be split further.

### F6. AC load without power tags (≈ 72 kWh/day)

- **What:** the grid converters' AC output (`marpower__450000_dynamic_conv_ps/sb_general.totalactivepower__value`,
  W) averages 13.3 kW, or 319 kWh/day. The power tags, without the double-counted feeders, add up to about
  247 kWh/day.
- **Meaning:** about 72 kWh/day of AC load has no tag, or no metadata.
- **Known part:** the consumers behind 10P3 (forward guest corridor) are measured only at the feeder:
  washers, dryers, crew-mess dishwasher, crew cabin sockets, crew mess JB, toilets. The topic
  `power-tags/10P3/washer-1` publishes without metadata, and its values are empty.

### F7. Unmeasured 700 VDC consumers, measured per bus segment

- **What:** none of these 700 VDC consumers has a power signal in Greptime or in the IO list: compression
  chiller (30.11), domestic water heaters 1–18 (25.41), power packs 1 and 2 (22.61/22.62), steering power
  pack (15.11), lube oil pumps (22.11/22.12), general service pumps 1–3 (34.11–34.13), about 40 winches,
  feeders and furlers on DB-HDC02–06, and the anchor winches. But all 8 DC ring switches (05.71–05.78)
  report current and voltage on both sides (`marpower__450000_dc_distribution__dc_switch`, `dcc_s_0/1`,
  `dcv_s_0/1`). Power that flows into a segment and doesn't flow out is used by that segment.
- **Switch orientation:** the documents don't say which segment is on section 0 of each switch. I fitted it
  from the data (sign of the flow in the direction 0571 → 0578):

  | 0571 | 0572 | 0573 | 0574 | 0575 | 0576 | 0577 | 0578 |
  |---|---|---|---|---|---|---|---|
  | + | − | − | − | − | − | − | + |

  With these signs, each segment's load follows its known consumers at a coefficient close to 1 (battery
  converters 0.90–0.99, ESI 0.79–0.89, grid converters 0.84–0.91). Every switch gets the same sign from both
  segments it borders. The two cable segments, which have nothing connected, read −0.4 and −0.8 kW: that is
  the measurement error.
- **Result (7-day average, ESI at its DC value):**

  | Segment | Unmeasured | Unmeasured consumers on it |
  |---|---|---|
  | SB.01.P01 | 1.4 kW · 34 kWh/day | Stern drive 13.11 (winding A), stern lube oil pump |
  | SB.01.P02 | 2.1 kW · 49 kWh/day | 24 VDC service bus, DB-HDC03, power pack 1, general service pumps 1–2, chiller, traveller winch |
  | SB.01.P03 | 1.3 kW · 31 kWh/day | 24 VDC emergency bus, DB-HDC02 (incl. steering power pack), water heaters 4–9 and 18 |
  | SB.01.P04 | 2.0 kW · 48 kWh/day | Stern drive 13.11 (winding B) |
  | SB.02.P01 | 1.7 kW · 42 kWh/day | Bow drive, fwd lube oil pump, DB-HDC04, 24 VDC buses, general service pump 3, power pack 2 |
  | SB.02.P02 | 1.25 kW · 30 kWh/day | Bow drive (2nd winding), DB-HDC05/06 (incl. anchor winches), water heaters 10–17 |
  | Cables (offset) | −1.2 kW | – |
  | **Total** | **≈ 8.6 kW** | |

- **Meaning:** about 2.8 kW of this is the 24 VDC converters' input (F4). Their variation is too small to
  tell which segment feeds which converter. That leaves about 5.8 kW, or 140 kWh/day, of truly unmeasured
  consumers. On 5 Nov, SB.01.P01 used 227 kWh: the stern drive was in use. The 15 water heaters and the
  chiller sit on segments that use only 1.3–2.1 kW in total, so in November they hardly run.
- **How found:** 1-minute averages of switch power (current × voltage, averaged over both sides), battery
  power per Brightloop group, ESI, grid converters and 350 V converters. Per segment, a least-squares fit
  of the segment load on its known consumers, for every combination of switch signs.

### F8. As built differs from the functional description: grid converter 05.12 is on SB.02.P01

- **What:** the functional description v5.0 places uGrid converter 05.12 on +SB.02.P02. In the data, its
  power shows up on SB.02.P01 (coefficient 0.91) and not on SB.02.P02 (0.07).
- **Meaning:** use the as-built placement in the segment model. Other placements in the document may be out
  of date as well, so check the model against the data.

### F9. Aradex `PvPower` doesn't match the power on the bus

- **What:** `marpower__150000_propulsion_ara.pv_power__value` (kW according to the IO list) has a
  coefficient of about 0.1 against the segment loads. The stern drive's use on 5 Nov is visible only in the
  segment balance.
- **Meaning:** this signal isn't the drive's DC power, or it's in other units. Check the Propulsion series
  (`pcs_*_ara*.power__value`) against the segment balance before relying on it.

### F10. Signals that stopped publishing, or never did

- `termodinamica__ac_misc` (`watt_ac_compressor_1/2`, `watt_sea_water_pump`, the compression chiller):
  last data 30 Oct.
- `marpower__450000_350vdc_system` (350 VDC per output): last data 27 Oct.
- `GeneralServicePump1Power` (KEB1) and `BackupGeneralServicePumpPower` (KEB2): in the IO list (read through
  Modbus), but with no MQTT topic.
- Battery groups 5-45 and 5-46 (forward batteries): no data in the analysed week. This may be on purpose;
  the SoC panels depend on it.

### F11. THRS pumps and technical-space fans: don't add

- **What:** `marpower__thrs__pumps.power_input__value` (18 pumps, ≈ 23 kWh/day) and
  `marpower__350000_ventilation.motor_inp_power__value` (supply and exhaust fan) report power.
- **Meaning:** they are most likely fed from breakers that already have power tags (EREC 1/2 power supply,
  technical space ventilators). Adding them would double count. Use them only to split a sub group further,
  after confirming in Eplan which breakers feed them.

## Proposed classification

| Data | Main group | Sub group |
|---|---|---|
| Compression chiller (when it publishes again) | HVAC | Chiller (new) |
| 350 VDC converters | Domestic | Lighting (new) |
| 24 VDC converter output minus breaker-level total | Technical | 24VDC unallocated (new) |
| Consumers behind 10P3 (until they have tags: the 10P3 feeder) | Domestic | Laundry (new), Crew; toilets → Technical / Black water |
| Grid converter AC output minus power tags | Technical | AC unallocated (new) |
| Segment remainder SB.01.P01 and SB.01.P04 | Propulsion | Thrusters (unallocated) |
| Segment remainder SB.01.P02, P03, SB.02.P01, P02 | Technical | 700VDC unallocated (new), one per segment |
| Aradex thrusters (existing data) | Propulsion | Thrusters (new sub group for existing data) |
| Future: winches, feeders, furlers, power packs | Propulsion | Sail handling (new) |
| Future: steering power pack, lube oil pumps | Propulsion | Steering, Lube oil (new) |
| Future: water heaters | Technical | Fresh water (alternative: Domestic / Hot water) |
| Future: general service pumps 1–3 | Technical | Bilge/FiFi |
| Future: anchor winches, pop-up deck winches | Technical | Deck equipment (new) |
| ESI (AC − DC), grid converters (DC − AC), 24 VDC converters, cable offset | **Losses** (new main group) | ESI, Grid converters, 24VDC converters, Measurement |

## Open items

| # | Item | Type | Who | Finding |
|---|---|---|---|---|
| 1 | Give the 10P1 and 10P2 feeder tags no main group | Bug fix (metadata) | Data | F1 |
| 2 | Rebuild the Aradex views on greptime-zero, and guard against the column type change | Bug fix (dbt) | Data | F2 |
| 3 | Book shore at the ESI DC side; add the AC − DC difference as Losses | dbt + dashboards, PR #996 | Data | F3 |
| 4 | Add 24 VDC converter output, and the remainder after breakers | dbt + metadata | Data | F4 |
| 5 | Add the 350 VDC converters | dbt + metadata | Data | F5 |
| 6 | Add grid converter AC output, the AC remainder, and grid converter losses | dbt | Data | F6 |
| 7 | Give the 10P3 feeder a better class; add metadata for `power-tags/10P3/washer-1` | Metadata | Data | F6 |
| 8 | Model the DC ring segments (signs from F7, 05.12 on SB.02.P01) | dbt | Data | F7, F8 |
| 9 | Add the Losses main group to the dashboards | Dashboards | Data | F3, F6, F7 |
| 10 | Check Aradex `PvPower` and PCS `power__value` against the segment balance | Analysis | Data | F9 |
| 11 | Restart the Termodinamica chiller feed (`termodinamica__ac_misc`) | Data collection | Zero / Termodinamica | F10 |
| 12 | Restart the 350 VDC DcOpp feed (`marpower__450000_350vdc_system`) | Data collection | Marpower | F10 |
| 13 | Publish general service pump power (KEB1, KEB2) over MQTT | Data collection | Marpower | F10 |
| 14 | Confirm in Eplan which breakers feed the THRS pumps and technical-space fans | Check | Electrical | F11 |
| 15 | Confirm whether battery groups 5-45 / 5-46 are offline on purpose | Check | Crew / Marpower | F10 |
| 16 | Ask Marpower to confirm the switch orientation (F7) | Check | Marpower | F7 |
| 17 | Find out whether winch drives and power packs can report electrical power | Data collection | Sail-hydraulic PLC supplier | F7 |
| 18 | Decide: water heaters under Technical / Fresh water or Domestic / Hot water | Decision | Team | Classification |

## Plan

Each step is a separate PR unless noted. Steps 1–3 correct what the dashboards show today; steps 4–7 add
what is measured; steps 8–9 make the remainder visible; step 10 runs alongside.

1. **Fix the double counting (item 1).** Set `main_group` to NULL for PT135Q01 and PT335Q01 in
   `load_power_tag_metadata.sql`. Silver already drops rows without a main group. Check: Technical drops by
   about 74 kWh/day; the 10P1/10P2 sub groups don't change.
2. **Fix the Aradex views (item 2).** Rebuild the Aradex staging/silver/gold models on greptime-zero. Cast
   `power__value` to DOUBLE in staging, so a future type change doesn't break the view again. Check: the
   Propulsion and Hydrogeneration series appear on Zero.
3. **Shore at DC level (item 3, extends PR #996).** In `stg_marpower__esi` / `slv_shore_power_converters`,
   add `esi_battery_current__value` and the bus voltage. Book DC power as Shore, and AC − DC as Losses / ESI.
4. **Losses main group (item 9).** Add 'Losses' to both dashboards: production/consumption graphs, flow
   diagram, treemaps. Decide whether it is shown with the consumers or separately.
5. **24 VDC total (item 4).** Gold model with converter output per minute; the remainder after the
   breaker-level total goes to Technical / 24VDC unallocated.
6. **350 VDC (item 5).** Staging/silver/gold for the four 350 V converters → Domestic / Lighting.
7. **AC side (items 6, 7).** Gold model with grid converter AC output; AC remainder → Technical /
   AC unallocated; grid converter DC − AC → Losses / Grid converters. Reclassify the 10P3 feeder; add
   metadata for the 10P3 tags that appear.
8. **DC ring segments (item 8).** `slv_dc_ring_segments`: per minute, the load per segment from the switch
   flows (signs in F7), minus the measured consumers on that segment (batteries, ESI DC, grid converters,
   350 V converters). Remainders in gold per the classification table. Test: the two cable segments stay
   within ±1.5 kW. Keep the switch signs in a seed-like metadata table, not in SQL.
9. **Balance check.** One query or panel that compares production (shore DC + solar + hydro + battery
   discharge) with consumption + losses. After step 8 the difference should be the measurement error
   (≈ 1 kW).
10. **Requests and checks (items 10–18).** Send items 12, 13, 16 to Marpower and 11 to Termodinamica; do
    items 10, 14, 15 and decide 18. As new signals arrive, move load from the "unallocated" sub groups to
    named ones.

## Appendix: key tables and signals

| Purpose | Table | Columns |
|---|---|---|
| DC ring switches | `marpower__450000_dc_distribution__dc_switch` (topics `keb*-05xx`) | `dcc_s_0__value`, `dcc_s_1__value` (A), `dcv_s_0__value`, `dcv_s_1__value` (V) |
| ESI shore | `marpower__450000_dc_distribution_esi` | `esi_ac_bus_active_power_3_phase__value` (kW), `esi_battery_current__value` (A, DC side) |
| Batteries | `views.gld_batteries_per_minute` | `avg_battery_power` (kW, + = discharging), topic group `5-41`…`5-46` = Brightloop 05.41…05.46 |
| Grid converters DC | `marpower__450000_dynamic_conv_ps_ara__5_11_u101`, `…_sb_ara__5_12_u101` | `pv_power__value` (kW) |
| Grid converters AC | `marpower__450000_dynamic_conv_ps_general`, `…_sb_general` | `totalactivepower__value` (W) |
| 350 VDC converters | `marpower__450000_dc_distribution__350v_conv_aft_1/2`, `fwd_1/2` | `hvdc_power__value` (W) |
| 24 VDC converters | `marpower__450000_24vdc_system`, topics `conv/w14e*` | `power__value` (W) |
| Chiller | `termodinamica__ac_misc` | `watt_ac_compressor_1/2`, `watt_sea_water_pump` |

## Additions

Everything above is the analysis and plan of 11 Nov 2026, kept as it was. New findings (F12 and on), status
updates and changes to the plan are added below, each with its date. Where an addition differs from the text
above, the addition applies.

### Status (2026-11-16)

- **PR #996 is merged and deployed** (10 Nov). Step 3 no longer extends it; see the PR grouping below.
- **The 350 VDC per-output feed is back** since 12 Nov (open item 12 is resolved). The topics are now
  `marpower/450000-350vdc-system/350vdc-dcopp{1,2}-m{0,1,2}`, with `pos_line_power` and `neg_line_power` per
  output. The `m2` modules publish far fewer rows than the others (1.5–3k against 11–13k per day).
- **The chiller feed** (`termodinamica__ac_misc`) is still stopped since 30 Oct (open item 11).
- **No 10P3 sub-tags publish any more**, `power-tags/10P3/washer-1` included. The 10P3 feeder is the only data
  for that panel.
- **The ESI DC current** (`esi_battery_current__value`) publishes on all four modules.
- **Unchanged:** the Aradex views still fail (F2), and the 10P1/10P2 feeders are still counted twice (F1).

### F12 (added 2026-11-16): a cast doesn't protect a Greptime view against a type change

- **What:** a Greptime view stores its plan with the types of the raw columns it reads. When a column type
  changes, the view fails, also when it casts the column (`CAST(power__value AS DOUBLE)`). Views on top of
  it fail too, because they hold the upstream plan inline. `CREATE OR REPLACE VIEW`, which is what our dbt
  view materialization runs, repairs a view; the views on top of it need the same, which a full `dbt build`
  does in order.
- **Why the Aradex views broke:** on Zero, `power__value` in the four `marpower__150000_propulsion__pcs_*_ara*`
  tables was changed from `BIGINT` to `DOUBLE` in place (the tables date from August). Nothing in this
  repository changes it. The committed snapshot still had `BIGINT`, so a local build never showed the error.
- **How found:** reproduced on a local Greptime 1.1.3 (the version on Zero) with a scratch table and views.
  The Aradex logic, run inline on Zero's raw tables, works: 22.5 kWh propulsion on 9 Nov, 2.2 kWh on 10 Nov.
- **Meaning:** step 2 changes, see below. A broken view returns an error rather than wrong numbers; the
  freshness check in the new step 9 makes it visible.

### F13 (added 2026-11-16): the metadata test treats "no main group" as missing metadata

- **What:** `tests/assert_power_tags_have_metadata.sql` failed for every tag whose `main_group` is NULL. With
  step 1 as planned, `dbt build` would fail on the two feeders.
- **Meaning:** a tag with `main_group` NULL now means *excluded on purpose*; the test fails only for a tag
  without a metadata row. Both files say so in a comment.
- **Also:** the energy report notebook (`notebooks/energy_report.py`) already left out all distribution-panel
  feeders by name, the 10P3 feeder included. It doesn't change with step 1.

### F14 (added 2026-11-16): the 450000 topic cut-over changes the source tables of steps 3 and 5–8

- **What:** Marpower moves the 450000 devices to a new topic convention. Vector stores those in one table per
  kind, `marpower__<system>__<kind>`, with the instance in `technical_name` (PR #1050, merged). Open PRs move
  the dbt models over: #1054 (24 V, batteries, solar converters) and #1057 (shore converters, to
  `marpower__dc_700v__shore_converter`). The history before the cut-over arrives later with a Greptime
  migration. On 16 Nov the new tables don't exist on greptime-zero yet.
- **Not affected:** `power_tags` (step 1), the Aradex tables (`marpower__150000_…`, step 2), the chiller.
- **Meaning:** steps 3 and 5–8 are built on the new tables, after the cut-over. Their checks need about 7
  days of data: either after the history migration, or on the days published after the cut-over.

### F15 (added 2026-11-16): orphan views on greptime-zero

- **What:** dbt doesn't drop the view of a model that was renamed or removed. These views on greptime-zero
  have no model in the repository, and nothing in the repository reads them:

  | View | State on 16 Nov |
  |---|---|
  | `views.gld_aradex_power_per_minute` | fails (F12) |
  | `views.gld_electrical_power_consumption_per_minute` | works |
  | `views.gld_24vdc_power_per_minute` | works |
  | `views.gld_power_tags_active_power_per_minute` | works |
  | `views.slv_power_tags_no_metadata` | works |

- **Action:** drop them by hand after a check that no Grafana panel saved outside this repository uses them:

  ```sql
  DROP VIEW views.gld_aradex_power_per_minute;
  DROP VIEW views.gld_electrical_power_consumption_per_minute;
  DROP VIEW views.gld_24vdc_power_per_minute;
  DROP VIEW views.gld_power_tags_active_power_per_minute;
  DROP VIEW views.slv_power_tags_no_metadata;
  ```

### F16 (added 2026-11-16): the segment remainders add up to the balance gap by definition

- **What:** every ring switch borders two segments, with opposite signs. Summed over all 8 segments, the
  switch flows cancel. So the sum of all segment remainders (step 8), the two cable segments included,
  equals production minus the measured consumers, whatever the switches read. The switches decide *where*
  the unmeasured load is, not *how much* there is.
- **Meaning:**
  - Booked anywhere, the cable offset would make production equal consumption + losses by definition.
    It stays out of every group, Losses included.
  - After step 8, a stopped feed doesn't show up as a balance gap: its load moves into the unallocated
    remainder of its segment. Step 9 changes accordingly, see below.

### Changes to the plan (2026-11-16)

**PR grouping.** This replaces "each step is a separate PR". The doc goes to main with PR A; each PR adds
its line to the work log; PR D deletes the doc, and a comment on ZERO-2619 links its last version.

| PR | When | Steps |
|---|---|---|
| A | now | 1, 2, 4 |
| B | after the cut-over (F14) | 5, 6, chiller |
| C | after the cut-over | 7 |
| D | after the cut-over and #1057 | 3, 8, 9 |

All PRs follow the current dbt pattern (staging → silver → gold views, per minute). The performance work
(ZERO-2620) changes that pattern later; this ticket doesn't anticipate it.

**Step 2.** No cast (F12). Update the four Aradex snapshot files from Zero, and rebuild all views with a full
`just dbt-deploy zero` after the merge.

**Step 3.** Moves to PR D, on the new shore converter table from #1057. The segment model needs the ESI at
its DC value, so step 3 belongs with step 8.

**Step 4: Losses.**

- A consumer main group: positive power, shown in every panel with consumer data on both dashboards: the
  production/consumption graphs, the flow diagram and the treemaps. It is added in PR A and stays empty until
  its first source arrives.
- The flow diagram's background image gets a fifth consumer row for Losses.
- Sub groups are named after the source: *Shore converters* (PR D), *Grid converters* (PR C),
  *350 VDC converters* (PR B, if the per-output data checks out), *24 VDC converters* (PR D). Losses that may
  come later and aren't conversion losses (cables, batteries, standby use) go under Losses as well.
- The measurement offset of the cable segments is not a loss (F16). It replaces "Measurement" in the
  classification table and is shown only in the balance check.

**Classification.**

- No sub group with a single consumer, unless that consumer is very significant. Exception: the chiller.
- One unallocated sub group per main group instead of one per segment: *Technical / 700VDC unallocated* for
  SB.01.P02, P03, SB.02.P01 and P02, and *Propulsion / Thrusters (unallocated)* for SB.01.P01 and P04. The
  split per segment is shown only in the balance check.
- The 10P3 feeder becomes *Domestic / Crew & laundry*: one tag can't be split further.
- *HVAC / Chiller* gets its own sub group. It is modelled in PR B and stays empty until the feed is back; in
  PR D the segment model subtracts it from SB.01.P02.
- Water heaters (open item 18): parked until they have a power signal. They are 15–18 units, so either class
  meets the sub-group rule. PR D puts a comment in the segment metadata at SB.01.P03 and SB.02.P02.

**Step 6.** Includes the split per 350 VDC output, now the feed is back, if the outputs add up to the
converter total. Input minus outputs becomes *Losses / 350 VDC converters*.

**Step 7.** No metadata for `power-tags/10P3/washer-1`: the topic no longer publishes.

**Step 9.** A plain production minus consumption panel shows the cable offset only (F16). Instead:

1. **Cable offset:** the sum of the two cable segments, as the quality of the switch measurements, within
   ±1.5 kW.
2. **Unallocated 700 VDC:** in total and per segment, over time. A sudden step points to a stopped feed, a
   double count or a type error.
3. **Freshness:** the age of the last sample for every source of a main group, so a stopped feed or a
   broken view is named directly.

### Status (2026-11-18)

- **PR A (#1085) is open.** The 450000 stack (#1052 → #1051 → #1055 → #1054 → #1053 → #1057) is approved but
  not merged, and none of the new per-kind tables exist on greptime-zero yet.
- **The chiller feed** is still stopped (open item 11).

### F17 (added 2026-11-18): the 350 VDC converters also move with the 450000 cut-over

- **What:** F14 lists steps 3 and 5–8 as affected, but the device list in #1054 also has the 350 VDC
  converters (`marpower/45-dc-350v/dc-dc-converter/02-71-t101` … `02-72-t102`) and the DcOpp outputs
  (`45-dc-350v/breaker/02-7x-u10x`). Today their data is only in the old tables
  (`marpower__450000_dc_distribution__350v_conv_*`, `marpower__450000_350vdc_system`).
- **Meaning:** step 6 waits for the cut-over as well. Only the chiller doesn't depend on it.

### F18 (added 2026-11-18): the chiller reports kW, and its data covers four test days

- **What:** the Termodinamica IO list (`zero-termodinamica/docs/Vent en AC lijst Termodynamica.xls`) and the
  bridge (`zero-termodinamica/modbus_bridges.json`) describe registers 182–184 (`watt_ac_compressor_1/2`,
  `watt_sea_water_pump`) as "1=0,01 Watt". The stored values are kW:
  - power / current (registers 185–187, "1=0,01 Ampere") is 239 V for all three devices, on every day;
  - on 26 Jun 2026 (240 minutes, chiller 0–6.8 kW) the load of segment SB.01.P02 (switches 05.72/05.73)
    followed the chiller at 0.93 kW per kW, r = 0.996;
  - the seawater pump reads up to 0.69; its datasheet (9441204 TMD453) gives a motor output of 1.2–2.2 kW.
- **Coverage:** the power columns have values only from 26 Jun to 3 Jul 2026. The chiller ran on 26, 27, 29
  and 30 Jun, during working hours (≈ 6.2 kW with both compressors on); 28 Jun has no rows; 1–3 Jul reads 0.
  Since then the rows arrive with empty power columns, and since 30 Oct there are no rows (open item 11).
  Within a running window there is a sample every 20 s.
- **Checks that pass:** power against current and against compressor and pump speed agree (1–2 samples of
  4,020 differ, at start and stop); the two compressors are not copies of each other; no duplicate
  timestamps.
- **Odd:** `engine_box_p_gas` goes from ≈ 10 to 34.5 on 30 Jun and stays at exactly 34.5 until 3 Jul, while
  the seawater temperature keeps changing. This may be a trip that stopped the unit; the data doesn't say.
  In June the DC switches publish on other topics than now (`keb6-0572`, `keb6-0573`), at an implausible
  level (≈ −680 kW); only their difference was used.
- **Meaning:** the data is good enough to build and test the chiller models on, not to state its typical
  consumption. The models convert kW to W. The thermal test dashboard shows these columns with unit `watt`,
  so it reads 3 W instead of 3 kW; that is outside this ticket.

### Changes to the plan (2026-11-18)

**PR grouping.** PR B holds what doesn't depend on the cut-over: the chiller (ZERO-2688), on the current table
`termodinamica__ac_misc`, and two classification changes on existing data. It sits on top of PR A. Steps 5
and 6 move to a PR of their own after the cut-over (B2). The cut-over also moves the DC ring switches
(`45-dc-700v/dc-switch/05-7x-q101`, #1054) and the uGrid grid converters (`45-dc-ac/inverter/05-1x-u101`,
#1055), so steps 7–9 keep waiting, except for the 10P3 reclassification of step 7.

| PR | When | Steps |
|---|---|---|
| B | now, on PR A | chiller; 10P3 → Domestic / Crew & laundry (from step 7); Aradex → Propulsion / Thrusters |
| B2 | after the cut-over (F14, F17) | 5, 6 |
| C | after the cut-over | 7 without the 10P3 reclassification |

**Aradex.** The Aradex data gets the sub group *Thrusters* (classification table), in a sub-group gold view
that the treemaps read instead of the main-group view. The segment remainders of SB.01.P01 and P04 become
*Propulsion / Thrusters (unallocated)* in PR D, as planned.

**10P3.** The energy report notebook (`notebooks/energy_report.py`) leaves out every tag with "DISTR" in its
name, the 10P3 feeder included (F13). Since 10P3 has no tags behind it, the report misses ≈ 40 kWh/day of
Domestic. The notebook is not part of this ticket.

### Status (2026-11-23)

- **PR A (#1085) is merged**; PR B (#1089) is open, rebased on main.
- **The 450000 cut-over is on main** (#1051–#1057) **and on greptime-zero.** The new per-kind tables hold the
  history: the 24 VDC power supplies and the 350 VDC converters from 28 Aug, the 350 VDC outputs from 24 Sep.
  The old tables stop on 20 Nov. Steps 5 and 6 can go ahead (B2).
- **Open PRs on the same files** (none changes the logic of steps 5 and 6):
  - #1112 refreshes the 24 VDC snapshots and edits the staging YAML;
  - #1114 drops the not-null tests on the power tag gold views, after they ran Greptime out of memory in
    `dbt-deploy`;
  - #1115 drops the busbar source and edits the staging YAML and the snapshot list;
  - #1113 multiplies the Aradex power by 1000 instead of 100, so Propulsion goes up from 10 Nov on.

### F19 (added 2026-11-23): the 24 VDC remainder is ≈ 43 kWh/day

- **What:** on 14–21 Nov the 11 power supplies (`marpower__dc_24v__power_supply`, `power__value`, = V × I in W)
  deliver 2.53 kW, or 60.6 kWh/day. For the same days the breaker-level view gives 15.4 kWh/day, not the
  2.6 kWh/day of F4, which was read from the old tables. The remainder is 1.86 kW on average and 0.64–2.48 kW
  per minute, never below zero: **43.3 kWh/day**.
- **Per converter group:** the breakers cover most of W14E1_02 (511 of 594 W) and hardly any of W14E2_01
  (1 of ≈ 700 W).
- **Not used:** the 24 V battery on 14E2 (`marpower__dc_24v__battery`, −0.36 A at 27 V on average, ≈ 10 W) and
  the distribution boards, which publish no power.
- **Also:** about a fifth of the power-supply rows carry a valid power value. Per minute every supply has
  one, except in 2 of the 9,766 minutes.

### F20 (added 2026-11-23): 350 VDC: the outputs read 0, and the converters pass power back

- **Outputs:** the six DcOpp outputs publish rows: on the old topics, and since 20 Nov on
  `marpower__dc_350v__breaker`. But power, current and voltage read 0 since 7 Oct (aft) and 26 Oct (fwd).
  02-72-u101 has a few non-zero values until 12 Nov. The Status of 16 Nov ("the feed is back") counted rows,
  not values, so open item 12 is still open: the DcOpp outputs publish 0.
- **Converters** (`marpower__dc_350v__dc_dc_converter`, `hvdc_power__value` in W, positive from 700 VDC to
  350 VDC), averages on 14–21 Nov: 02-71-t101 380 W, 02-71-t102 −55 W, 02-72-t101 1,583 W, 02-72-t102
  1,237 W. Together that is 3.15 kW, or **75.5 kWh/day** (F5: 67 kWh/day on the old tables).
- **Power flows back:** per minute the aft pair ranges from −2.0 to +1.8 kW. Power goes into the 350 VDC
  network fwd and partly back to the 700 VDC bus aft. The sum over all four stays positive (one minute of
  9,764 at −1.4 W), so only that sum is the load of the 350 VDC network.
- **No losses from the converters:** high side minus low side power (hvdc power − lvdc V × I) is negative for
  both fwd converters (−50 and −85 W), so the converters' own measurements can't give their losses.
- **Meaning:** step 6 books the sum of the four converters' hvdc power as Domestic / Lighting, converter
  losses included. There is no split per output and no *Losses / 350 VDC converters* until the outputs
  report power.

### Changes to the plan (2026-11-23)

**B2** holds steps 5 and 6, on branch `feature/ZERO-2619-add-24vdc-350vdc`, on top of PR B (#1089).

- **Step 5:** `slv_24vdc_power_supplies` → `gld_24vdc_unallocated_power_per_minute_per_group`: per minute, the
  power-supply total minus the breaker-level total, as *Technical / 24VDC unallocated*.
- **Step 6:** `stg_marpower__dc_350v_converters` → `slv_350vdc_converters` →
  `gld_350vdc_power_per_minute_per_group`: the sum of the four converters, as *Domestic / Lighting*. There is
  no split per output and no *Losses / 350 VDC converters* (F20).
- Like the Aradex and chiller views, each has one gold view for the main group and the sub group panels.
- The new gold views have no dbt tests: as with the power tag gold views (#1114), a test aggregates the whole
  history.

### F21 (added 2026-11-23): bidirectional converters, and power that flows back

- **What:** all converters between the 700 VDC bus and its sources and loads, from the drawings and the
  functional descriptions, against Zero's data (sign and opposing flows):

  | Converter | Type | Connects | Data |
  |---|---|---|---|
  | Battery converters =05.41–05.46-T101 | Brightloop, 3 DC/DC channels per module, 80 A each | Battery strings (760–930 V) and the bus segments | 13 pack channels, −55 to +36 kW |
  | Shore converters =07.11-TBC1, =07.12-TBC1 | Marpower ESI AC/DC, 2 × 2 × 50 kW | Shore 400 VAC and SB.01.P01 / P04 | Never negative (14–21 Nov) |
  | uGrid =05.11-U101, =05.12-U101 | Aradex DC/AC inverter | Bus (SB.01.P04, SB.02.P02) and the 400 VAC switchboard, in parallel with droop load sharing | Never negative, no opposing flows (14–21 Nov) |
  | Thruster drives =13.11-U101/U102, =13.31-U101/U102 | Aradex DC/AC inverters | Bus and the thruster motors, also hydrogeneration | Split by sign (Propulsion / Hydrogeneration) |
  | 350 VDC converters =02.71/02.72-T101/T102 | Epic Power bidirectional DC/DC, 8 kW | Bus (aft SB.01.P04, fwd SB.02.P02) and the 350 VDC network; bus tie 02.71-Q001 closed | Aft converters negative in 19 % and 34 % of the samples (F20), also on the busbar topics since 1 Sep |
  | 24 VDC supplies 14E1, 14E2 | 700/24 VDC converters | Bus and the 24 VDC service and emergency boards; 14E2 also has two 24 V battery packs | Never negative; the 14E2 battery averages ≈ 10 W |

- **Battery packs charge each other:** from 1 Sep to 21 Nov, one pack discharges while another charges
  in 5,243 of 58,760 minutes (9 %), with about 15 kW passed between them on average. The EMS design
  (9445234-1, 7.1.3) first decides whether the system charges or discharges, then selects the packs; it
  doesn't describe packs charging each other.
- **The 350 VDC network passes power between bus segments:** with the bus tie closed, power goes in fwd
  (SB.02.P02) and comes out aft (SB.01.P04), up to about 2 kW (18 Nov).
- **Meaning:**
  - The flow diagram adds the charging and the discharging packs up separately, so in those minutes it shows
    both, about 15 kW too high on each side. The production and consumption graphs don't use the battery data.
  - The 350 VDC sum (step 6) is right; the losses of the loop are part of it.
  - PR D (step 8) subtracts each 350 VDC converter from its own segment, not the sum, and the battery
    converters per segment as measured.
  - Step 7 checks the two uGrids for opposing flows before it adds their AC output.
  - The 24 VDC battery is too small to matter for the 24 VDC remainder (F19).
- **Open items (new):**
  - 19: ask Marpower whether battery packs charging each other is intended (Marpower, check).
  - 20: ask Marpower / Epic Power whether the 350 VDC converters should share the load instead of passing
    power aft (Marpower, check).
  - 21: the flow diagram shows the net battery power per minute instead of the charging and discharging
    packs separately (Data, dashboards).

## Work log

| Date | PR | Step | What |
|---|---|---|---|
| 2026-11-16 | – | – | Plan checked against the code and greptime-zero; see the Additions above. |
| 2026-11-16 | A | 1 | 10P1/10P2 feeders get no main group; metadata test adjusted (F13). Removes 74.7 kWh/day from Technical (Zero, 9–16 Nov). |
| 2026-11-16 | A | 2 | Aradex snapshot files updated to `DOUBLE` (F12). Aradex logic checked inline on Zero. Views are repaired by the deploy. |
| 2026-11-16 | A | 4 | Losses added to the graphs and treemaps of both dashboards and to the flow diagram, whose background image gets a fifth consumer row. |
| 2026-11-17 | A | 4 | Losses icon in the flow diagram is now a corner-right-down arrow; Losses colour `#646464` (Grafana has no named grey). Consumers stack in their own group in both production/consumption graphs, so they show below zero also when there is production. Checked with 2 hours of Zero's data in a local Greptime. |
| 2026-11-18 | B | chiller | Status, F17, F18 and the PR B change added. Chiller models (`stg_termodinamica__ac_misc` → `slv_chiller` → `gld_chiller_power_per_minute_per_main/sub_group`) as HVAC / Chiller, kW converted to W; added to the graphs, flow diagram and treemaps of both dashboards. Checked with the chiller data of 26 Jun – 3 Jul in a local Greptime: 57.6 kWh, the same in every panel. |
| 2026-11-18 | B | 7 (part) | 10P3 feeder from Technical / Technical to Domestic / Crew & laundry. Checked on 9 Nov 08:00–14:00 in a local Greptime: 12.8 kWh moves. |
| 2026-11-18 | B | classification | Aradex in the sub group Propulsion / Thrusters (`gld_aradex_power_per_minute_per_sub_group`), read by both treemaps. Same totals as the main-group view on 9 Nov 08:00–14:00 (Propulsion 87.0 kWh, Hydrogeneration 0.2 kWh). |
| 2026-11-23 | B | review | One gold view each for the Aradexes and the chiller, `gld_aradex_power_per_minute_per_group` and `gld_chiller_power_per_minute_per_group`, read by the main group and the sub group panels; their sub group is a constant, so a separate main-group view saves nothing. Not `gld_aradex_power_per_minute`: that name is an F15 orphan view. After the deploy, drop `views.gld_aradex_power_per_minute_per_main_group` on greptime-zero by hand, as the views of F15. |
| 2026-11-23 | – | – | Status, F19, F20 and the B2 change added: cut-over and history on greptime-zero, open PRs on the same files, the 24 VDC remainder, the 350 VDC outputs reading 0. |
| 2026-11-23 | B2 | 5 | `slv_24vdc_power_supplies` → `gld_24vdc_unallocated_power_per_minute_per_group` (Technical / 24VDC unallocated: power supplies minus breakers per minute), in the graphs, flow diagram and treemaps of both dashboards. Checked on 18 Nov 08:00–14:00 in a local Greptime: 15.6 kWh from the power supplies, 4.3 kWh behind breakers, 11.3 kWh unallocated, the same in every panel and as computed on Zero. |
| 2026-11-23 | B2 | 6 | `stg_marpower__dc_350v_converters` → `slv_350vdc_converters` → `gld_350vdc_power_per_minute_per_group` (Domestic / Lighting: the sum of the four converters), in the same panels. Checked on the same window: 20.5 kWh, the same in every panel and as computed on Zero. No split per output and no 350 VDC converter losses (F20). |
| 2026-11-23 | – | – | F21 added: converter types and connections from the drawings, battery packs charging each other, the 350 VDC network passing power between segments; open items 19–21. |
