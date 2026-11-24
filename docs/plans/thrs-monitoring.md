# Plan: THRS Monitoring page (DHW)

Temporary: delete this file when the work is done.

A native zero-ui page at `/thrs/monitoring/:module` that rebuilds the Grafana Heat System trends for the crew, with mode and state history next to them. The first version covers DHW only. The [Figma mockup](https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=11817-68357) sets style and layout; [`heat-system-dashboard.json`](../../zero-dashboards/dashboards/Commissioning/heat-system-dashboard.json) sets the data (tables, aggregates, units).

## Where we are

**Update 2026-11-23:** thrs-api was removed on `main` ([#1099](https://github.com/foundation-zero/zero/pull/1099)) while this page was built in it. The page now calls its own API address, and [ADR 0003](../adr/0003-thrs-monitoring-api.md) proposes where that API runs; the decisions below that name thrs-api describe where it was built, not where it will run. The history work below was done on `design-playground` and brought onto `main` in one change.


- **No history in the browser.** zero-ui reads live values from GraphQL services and sees history only through Grafana iframes. `thrapp/stores/history.ts` keeps the latest value, not history.
- **`thrs-api`** (the `api` target of zero-thrs-control) runs apart from the control loops. It has no GreptimeDB connection and no history fields.
- **Prior art:** zero-domestic-control reads GreptimeDB over MySQL (`src/domestic_control/history.py`, `GREPTIME_URL=mysql://…:4002/public`) and exposes fixed-bin logs through Strawberry.
- **Charts:** zero-ui has `echarts` and `vue-echarts`. `common/components/time-based-chart/` holds two unused ECharts components.
- **Storybook** is set up on `design-playground` but not committed yet (`zero-ui/.storybook/`, `package.json` changes).

Measured on live `greptime-zero` on 2026-11-10 (server-side execution time):

| Query | 6 h | 24 h | 7 days |
| --- | --- | --- | --- |
| DHW temperatures, binned | 26 ms | 74 ms | 760 ms |
| Boost mode change points | 18 ms | 33 ms | 138 ms |
| Tank 1 state change points | 199 ms | 341 ms | 1,625 ms |

## Data sources (DHW)

| Page part | Table (`public.`) | Columns |
| --- | --- | --- |
| Boost mode | `thrs__controller__dhw__control_mode` | `automatic_mode__boosting_mode` (null = Manual) |
| Filling mode | same | `automatic_mode__filling_mode` (null = Manual) |
| Tank states | `marpower__thrs__tank_controllers` | `tank_{1,2,3}_state__value` |
| AMCS badge | live `dhw.sensorValues.mode` (from `marpower__thrs__amcs_modes`) | 0 AMCS Local, 1 AMCS Manual, 2 AMCS Auto, 3 Advisory (`EXTERNAL` in code) |
| Min/max lines | `thrs__controller__dhw__parameters` | `minimum_/maximum_tank_temperature`, `minimum_/maximum_tank_level` |
| Trends | `marpower__thrs__{temperatures,level_sensors,pumps,valves,flows,pressures}` | as in the Grafana panels, filtered on topic `marpower/500000-thrs/dhw/%` |
| Device labels | the sensor tables' `yard_tag` | `[yard_tag] technical_name`, as in Grafana |

`thrs__controller__dhw__controller_state` stopped receiving data on 2026-10-27, so tank state history only starts from the `tank_controllers` table.

The tank temperature chart uses `dhw-temperature-tank{1,2,3}`. The Temperatures section uses all ten DHW temperature devices.

## Decisions

- **Endpoint:** typed history resolvers in `thrs-api` read GreptimeDB over MySQL. The client never sends table or column names; it picks a metric from a fixed list, and the server maps it to its table, column, aggregate and device filter.
- **Series:** values are binned to about 400 points per series, with round bin sizes (1 s, 5 s, 10 s, 30 s, 1 m, 5 m, 10 m, 30 m, 1 h…). Gaps longer than 5 minutes are drawn as breaks.
  - Aggregates follow Grafana: AVG for most, MAX for quantity, energy and operation time.
  - Each device also gets its last raw value and timestamp for the table beside the chart.
- **States:** the server returns segments it has already merged (`{state, start, end}`) and the total time per state, clipped to the range. It includes the state that was active when the range starts.
- **Parameters:** min/max come back as change points and are drawn as stepped lines.
- **GreptimeDB is an optional dependency** under [ADR 0001](../adr/0001-dependency-outages.md). If it is down, the monitoring fields return an error and the rest of `thrs-api` keeps serving. It doesn't affect readiness.
- **Colours:** the mimics' `ModeBadge` tables (`MODE_COLORS`, `DHW_TANK_MODE_MODES` and the DHW boost and filling maps). Manual uses `ModeBadgeMode.ManualControl` (`--warning`). Bands behind the trends sit at about 10% opacity.
- **Header:** the current boost mode badge, the AMCS badge and the alarms count, all read-only. It has no Automatic control toggle.
- **Time bar:** pinned below the header and shared by the whole page.
  - Default range is the last 6 h, with a 30-day maximum.
  - Back, forward and zoom-out buttons.
  - The range is stored in the URL query string.
  - While the range ends at "now", it refreshes every 30 s and only fetches the new data.
- **Performance budget:** up to 24 h, the first charts appear within 1 s and the whole page within 3 s; up to 7 days, the whole page within 5 s. Each section is one parallel GraphQL request.

## Steps

Three PRs, in order. Each one can be merged on its own.

### PR 0: commit the Storybook setup

Commit the Storybook work already on `design-playground` (`.storybook/`, `package.json`, the ESLint config and the Button story) as its own PR, so the component PR builds on it.

### PR 1: history resolvers in `thrs-api` (zero-thrs-control) — done locally

Built on `design-playground`, not pushed.

- **Config and engine:** `Config.greptime_url` (optional). The engine is created in the `create_app` lifespan and does not connect until the first query, so an unreachable GreptimeDB only fails the monitoring fields. The pool holds 30 connections, one full page load, so refreshes don't reconnect.
- **Registries** (`src/thrs/monitoring/sources.py`): `MonitoringMetric` (one per Grafana panel plus the four DHW parameter limits) and `MonitoringSignal` (boost mode, filling mode, tanks 1–3), mapped to table, column, aggregate and unit. Only these names reach the SQL; a test checks they are plain identifiers.
- **Bins** (`bins.py`) and **segments** (`segments.py`) as planned. A signal that stopped reporting for more than 5 minutes ends at its last sample.
- **Queries** (`history.py`): bound parameters for times, topic and devices. Labels use the sensor tables' own `yard_tag` column, so there's no join on `io_metadata`. The schema comes from the URL's database, not a hard-coded `public.`.
- **GraphQL** (`src/thrs/graphql/monitoring.py`):
  - `monitoringSeries(module, metrics, start, end, devices)` returns per metric `unit`, `step`, `binSeconds`, and per device `device`, `yardTag`, `times`, `values`, `latest`.
  - `monitoringStates(module, signals, start, end)` returns per signal `segments` and `totals`.
  - The end of the range is clipped to now, and ranges over 30 days are rejected.
- **No `monitoringAmcsMode`:** the live DHW query already returns the AMCS mode as `sensorValues.mode` (`SystemAmcsControlModeType`), so the page reads it from there.
- **Dependencies:** `aiomysql`, and `sqlalchemy[asyncio]` so `greenlet` is installed on every platform.
- **Tests:** unit tests for bins, segments, registries and resolvers, plus integration tests marked `greptime` that seed a throwaway GreptimeDB (`GREPTIME_TEST_URL`, skipped when it isn't reachable). The full suite passes when run serially; `tests/cli` doesn't tolerate `-n`.
- **Deploy:** `GREPTIME_URL` in docker-compose (defaults to live zero) and `.env.example`. In the chart, `greptime.url` is written to the configmap only when it is set.
- **Performance** (`scripts/monitoring_timing.py`, from a Mac over Tailscale, warm pool). Server-side, each query takes 10–30 ms; the rest is network and protocol.

  | Range | Whole page | First section | Budget |
  | --- | --- | --- | --- |
  | 6 h | 1.8 s | 0.2 s | 3 s / 1 s |
  | 24 h | 1.6 s | 0.5 s | 3 s / 1 s |
  | 7 days | 3.2 s | 1.1 s | 5 s |

  The first load after the API starts takes about 4 s while the pool connects. Tank states are the slowest section at 7 days; fetching the three tanks in one query is the fallback if that grows.

### PR 2: monitoring components (zero-ui) — done locally

Built on `design-playground`, not pushed. Code lives in `src/modules/thrapp/monitoring/`.

- **Mockup change:** the mockup gained an **Advisory mode** section (a distribution and a timeline of the AMCS mode). So `monitoringStates` now also serves `AMCS_MODE`, named `amcs_local`, `amcs_manual`, `amcs_auto` and `advisory`.
  - Colours: Local `Idle`, Manual `ManualControl`, Auto `AdvisoryOff`, Advisory `Active`.
  - The mockup's timeline in that card still shows boost-mode placeholder content; it's drawn as the AMCS timeline.
- **Refresh bins:** `monitoringSeries` takes an optional `binSeconds`, so a refresh fetches the newest part with the bin size the chart already shows. It must be a round bin and stay within 400 points.
- **Shared colours:** the DHW boost, filling and tank-state badge maps moved into `mode-badge.consts.ts`, which imports no store, so the charts can use them without the API client. The mimics behave as before.
- **Components**, each with stories for data, empty, loading and error, rendered in dark (default) and light through a new Storybook theme switch:
  - `TimeRangePicker`
  - `StateTimeline`: HTML bars; labels only where they fit, details in the hover title.
  - `StateDistribution`: an SVG donut plus a table.
  - `TrendChart`: ECharts on canvas. Mode bands are `markArea` at 7% fill, limits are stepped dashed lines in `--attention` with a stacked band between them, and the legend toggles lines.
  - `LatestValuesTable`
  - `MonitoringCard` and `MonitoringSection`
- **Colours in charts:** ECharts can't read `var()` or `oklch()`, so chart colours are resolved to rgba inside the chart's own element and resolved again when the `<html>` theme class changes. Series colours use the dataviz reference palette, validated against the zero-ui light (`#f4f9fe`) and dark (`#22272b`) surfaces; past eight series the hues repeat with a dashed line.
- **Data:** `monitoring-data.utils.ts` (`useMonitoringSeries`, `useMonitoringStates`) loads a range in full, and on refresh fetches from two bins (or one minute, for states) before the last load and merges that in. The shared range, refresh interval and refresh tick live in `stores/monitoring.ts`.
- **Tests:** 29 Vitest specs for range maths, URL round-trip, ticks, gaps, both merges, donut arcs, segment placement, the ECharts option and the incremental loader. The full zero-ui suite (368) passes; lint and vue-tsc are clean.

### PR 3: the page (zero-ui) — done locally

Built on `design-playground`, not pushed.

- **Route and navigation:** `thrs/monitoring/:module` with a Monitoring tab in `MainNav`. `ModuleTabs` only offers modules in `MODULE_MONITORING`, and any other module shows "not available yet".
- **Configuration:** `MODULE_MONITORING` in `monitoring.consts.ts` lists the DHW sections in mockup order.
  - State panels: advisory mode, boost and filling modes, and tank states.
  - Trend panels: tank temperatures and levels (tank devices only, with limits, levels with totals), then pumps (9 metrics), valves (3), flow (3), temperatures and pressure.
- **View (`views/Monitoring.vue`):**
  - The title and `TimeRangePicker` are pinned at the top of the page's own scroll area.
  - The range syncs both ways with `?range=&end=`.
  - One `monitoringStates` request covers all signals, shared by the state cards and the bands behind the trends. Each trend panel sends its own `monitoringSeries` request.
  - All charts share one ECharts cursor group.
- **Toolbar (`MonitoringStatus`):** the live AMCS mode (from the control query's `sensorValues.mode`) and the module's `ModeBadges`, read-only, without the Automatic control toggle.
- **Alarm count: not built.** thrs-api has no module-level alarm source (alarms exist only as per-sensor flags in the mimic data), so the header doesn't show the agreed alarm count. It needs an alarm aggregate in thrs-api first.
- **Checked locally:** zero-ui dev server with the new thrs-api against live zero.
  - Screenshots at 1920, 1440 and 1180 match the mockup's sections.
  - Fixed after the first look: band labels piling up where boost mode switches often (now only bands of 5% of the range or more are labelled), and value tables taller than their chart (now capped and scrollable, with truncated names).
- **Speed from this Mac over Tailscale:** warm `monitoringStates` requests take 0.4–0.7 s; a full page took 2.4 s for 6 h and 4.6 s for 7 days. Single requests sometimes spiked to 3–18 s after the API had been idle: stale pooled connections over Tailscale, plus GreptimeDB's own HTTP latency varying from 0.15 to 1.3 s from here. Pooled connections now recycle after 60 s. This still needs measuring on board, where thrs-api and GreptimeDB sit in the same cluster.

### PR 4: changes after the UX review — done locally

Built on `design-playground`, not pushed. The review notes were agreed point by point on 2026-11-23.

- **Layout and type:**
  - Advisory, boost and fill mode and the tank states sit under one "Modes & states" group, each with its own collapsible heading above its boxes.
  - Headings follow the design system: Headline 4 for the page title, Subhead 1 for groups, Headline 6 for panels.
  - Every timeline and chart has the same plot inset (`PLOT_INSET`), so the time axes line up down the page. Donuts, last values and totals sit in a 360 px column on the right.
- **Charts:**
  - Tooltips use the design system's tooltip style.
  - Dragging across any timeline or chart zooms to that stretch; the time picker takes a custom from/to as well as the quick ranges.
  - A legend click shows one line; further clicks add or remove lines; "Show all" resets.
  - Valves are grouped by circuit (HT boosting, heat pump boosting, the tank boosting valves both share, filling, hot water use) and temperatures by boilers, boosting circuit and filling preheat chain. A click on a group shows only that group.
  - Boost and fill mode overlays each have a switch, remembered per chart.
  - The range between the minimum and maximum parameters is drawn as rectangles held to the end of the range in the brand colour. Before, the stacked band stopped at the last parameter change and could vanish behind the axis edge.
  - Pumps open on flow, valves on relative position, flow on flow. The metric drop-down lists alphabetically.
- **Heat exchange:**
  - A `HEAT` metric from `marpower__thrs__heat_transfers` (topics `thrs/controller/<module>/…`, no yard tag, W scaled to kW).
  - The heat per source is stacked, with noise below zero clipped. Beside it, the energy each source delivered over the range and its share.
- **Water usage:** the fill line counters (`dhw-flow-dc`, `dhw-flow-drives`) become litres per period, with the volume per line and the total. Bars are drawn as custom rectangles, because ECharts' own bars widen the time axis out of line with the other charts.
- **Annotations:**
  - Crew notes are stored in `thrs__monitoring__annotations`, created on first use, in `GREPTIME_ANNOTATIONS_URL` (defaults to `GREPTIME_URL`).
  - THRS has no login, so the author is a name typed in the browser, and a random key kept in the browser lets only that browser delete its notes.
  - Parameter changes come from consecutive rows of `thrs__controller__<module>__parameters__set`; alarms from the change points of `marpower__500000_thrs__<module>__alarm`.
  - Each annotation shows as a line across every timeline and chart, with an icon that opens the note on hover. Filter chips per kind sit under the time picker.
  - Release annotations are left for later: nothing records releases yet.

### PR 5: second review round — done locally

Built on `design-playground`, not pushed.

- Group headings are in capitals, so they stand apart from the panel headings.
- Tooltips render on top of the page (`Teleport` to `body`, and ECharts' `appendTo: "body"`), so the edge of a tile no longer cuts them off.
- Heat exchange is its own group, second after Modes & states, with "Heat transfer" (the stacked chart and energy per source) and "Heat distribution" (a treemap beside a pie, both of the energy per exchanger over the range).
- Water usage shows fresh water in (`dhw-freshwater-flow-supply` from `marpower__thrs__calculated_flows`, served as the `CALCULATED_FLOW` metric) and hot water out as filled lines in L/min per period, with litres in, out and the change in tank volume. No meter measures hot water out; it is fresh water in less what the tanks gained, as the tanks only take in fresh water and only give out hot water.
- The last-values tables name devices in words without the module and kind ("HVAC exchanger return"), with narrower value and age columns, so the ten temperatures fit without scrolling.

## Open points

- The boat's `greptime.url` value, and whether it needs credentials, live in the cluster configuration (edge-flux), not in this repo. zero-domestic-control uses `mysql://app@…:4002/public` without a password.
- Pump flow on the boat reads around 10.9 million L/min, so that column's unit or scaling is off at the source.
- Hot water out is derived from the tank levels, so level sensor noise shows up in it; a flow meter on the hot water outlet would make it exact.
- Before annotations go live, check that the `app` user on the boat's GreptimeDB may create a table and write to it.
- Whether `boosting_low_temperature` (not implemented) should get a legend entry once it ships. Today it is hidden because it never has any time.
