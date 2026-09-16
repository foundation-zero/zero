//! Computed-field recompute (`COMPUTED_MODE=recompute`).
//!
//! thrs-api derives its `sensorValues` computed fields (pydantic
//! `computed_field`s) live from the raw sensor values on every read. The control
//! loop also publishes them to `{controller}/<module>/<field>`, which
//! `COMPUTED_MODE=relay` (the default) just relays - but that lags whenever the
//! loop hasn't ticked, so it can differ from thrs-api's fresh value. This module
//! reproduces thrs-api's formulas in-process, reading the same raw sensor topics,
//! so a recomputed field matches thrs-api's live value (numerically; float
//! serialization still differs by a display ULP, like every other float leaf).
//!
//! The computed fields of `thrusters`, `dhw` and `pvt` are ported (see
//! [`formula`] for the full table); every other (module, field) returns `None`
//! and the resolver falls back to relaying. The porting pattern: read raw leaves
//! -> compute with the generic helpers (`flow_sum`, `weighted_temperature`,
//! `heat_transfer`, ...) -> `Stamped.combine` picks the **min** input timestamp.

use std::collections::BTreeMap;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::{json, Value};

use crate::cache::TopicCache;

/// `4184 / 60` kW·min/(l·K) - THRS `WATER_HEAT_TRANSFER_CONVERSION`.
const WATER_HEAT_TRANSFER_CONVERSION: f64 = 4184.0 / 60.0;
/// `valves_open_closed` tolerance; a valve reads open above `1 - TOL`, closed
/// below `0 + TOL` (THRS `control.Valve.OPEN=1.0`, `CLOSED=0.0`).
const VALVE_TOL: f64 = 0.05;

/// One `Stamped<T>` value pulled from (or derived over) the cache: an optional
/// scalar plus the timestamp to carry forward.
#[derive(Clone)]
struct St {
    value: Option<f64>,
    ts: String,
}

/// Reads raw sensor leaves for one module out of the cache, addressing them by
/// the GraphQL field name (e.g. `thrustersFlowAft`) and raw leaf key (`Flow`).
pub struct InputReader<'a> {
    cache: &'a Arc<TopicCache>,
    topics: &'a BTreeMap<String, String>,
}

impl<'a> InputReader<'a> {
    pub fn new(cache: &'a Arc<TopicCache>, topics: &'a BTreeMap<String, String>) -> Self {
        Self { cache, topics }
    }

    /// The `{value, timestamp}` of a raw leaf, or `None` when the topic isn't
    /// cached (so a computed field that depends on missing input resolves null,
    /// like thrs-api reading an absent sensor).
    fn leaf(&self, field: &str, leaf_raw: &str) -> Option<St> {
        let topic = self.topics.get(field)?;
        let payload = self.cache.get(topic)?;
        let leaf = payload.get(leaf_raw)?;
        let ts = leaf.get("TimeStamp")?.as_str()?.to_string();
        // `Value` may be JSON null (an OptionalCelsius with no reading).
        let value = leaf.get("Value").and_then(Value::as_f64);
        Some(St { value, ts })
    }
}

/// Lexicographic min of the given timestamps, which for the wire's uniform
/// `...Z` (or all `+00:00`) form is the chronological min - matching THRS
/// `Stamped.combine`, which keeps `min(timestamp)`.
fn min_ts(stamps: &[&str]) -> String {
    stamps
        .iter()
        .filter(|s| !s.is_empty())
        .min()
        .map(|s| s.to_string())
        .unwrap_or_default()
}

/// `if x.value` in Python: a float is falsy when 0.0, `None` is falsy.
fn truthy(v: Option<f64>) -> bool {
    matches!(v, Some(x) if x != 0.0)
}

fn leaf_json(value: Option<f64>, ts: &str) -> Value {
    json!({ "Value": value, "TimeStamp": ts })
}

/// Current UTC time as Python `datetime.now(UTC).isoformat()` (microsecond
/// precision, `+00:00` offset) - the shape THRS `Stamped.stamp(value)` produces.
/// Used only where thrs-api itself stamps a computed field with read-time `now()`
/// (a valve-gated device's off-branch `Stamped.stamp(0)`), so mqtt-graphql
/// reproduces that behaviour rather than a stale input timestamp. Being read-time
/// `now()`, it is inherently non-reproducible across two reads - the sections
/// parity suite compares such computed timestamps with a tolerance.
pub fn now_iso() -> String {
    let d = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default();
    let secs = d.as_secs() as i64;
    let micros = d.subsec_micros();
    let (hh, mm, ss) = (
        (secs.rem_euclid(86400)) / 3600,
        (secs.rem_euclid(86400) % 3600) / 60,
        secs.rem_euclid(86400) % 60,
    );
    // Howard Hinnant's days->civil algorithm (proleptic Gregorian).
    let z = secs.div_euclid(86400) + 719_468;
    let era = if z >= 0 { z } else { z - 146_096 } / 146_097;
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let day = doy - (153 * mp + 2) / 5 + 1;
    let month = if mp < 10 { mp + 3 } else { mp - 9 };
    let mut year = yoe + era * 400;
    if month <= 2 {
        year += 1;
    }
    format!("{year:04}-{month:02}-{day:02}T{hh:02}:{mm:02}:{ss:02}.{micros:06}+00:00")
}

// ---------------------------------------------------------------------------
// thrusters
// ---------------------------------------------------------------------------

const THRUSTERS_FLOWS: [(&str, &str); 2] =
    [("thrustersFlowAft", "Flow"), ("thrustersFlowFwd", "Flow")];
const THRUSTERS_TEMPS: [(&str, &str); 2] = [
    ("thrustersTemperatureAft", "Temperature"),
    ("thrustersTemperatureFwd", "Temperature"),
];

/// `thrustersFlow` = `CalculatedFlow.from_summed_sensors(flow_aft, flow_fwd)`.
fn thrusters_flow_st(r: &InputReader) -> Option<St> {
    flow_sum(r, &THRUSTERS_FLOWS)
}

fn thrusters_flow(r: &InputReader) -> Option<Value> {
    Some(flow_leaf(thrusters_flow_st(r)?))
}

/// `thrustersTemperatureRecovery` =
/// `CalculatedTemperature.from_weighted_sensors([flow_aft, flow_fwd],
/// [temp_aft, temp_fwd], default=None)`: flow-weighted average of the two
/// temperatures, null when there is no flow.
fn thrusters_temperature_recovery_st(r: &InputReader) -> Option<St> {
    weighted_temperature(r, &THRUSTERS_FLOWS, &THRUSTERS_TEMPS)
}

fn thrusters_temperature_recovery(r: &InputReader) -> Option<Value> {
    Some(temp_leaf(thrusters_temperature_recovery_st(r)?))
}

/// `thrustersTemperaturePreCooler`: the recovery temperature when both thruster
/// switches are open; the recovery-mix temperature when both are closed;
/// otherwise unknown (null), carrying the switches' min timestamp.
fn thrusters_temperature_pre_cooler_st(r: &InputReader) -> Option<St> {
    let sw_fwd = r.leaf("thrustersSwitchFwd", "PositionRel")?;
    let sw_aft = r.leaf("thrustersSwitchAft", "PositionRel")?;
    let (pf, pa) = (sw_fwd.value.unwrap_or(0.0), sw_aft.value.unwrap_or(0.0));
    let both_open = pf > 1.0 - VALVE_TOL && pa > 1.0 - VALVE_TOL;
    let both_closed = pf < VALVE_TOL && pa < VALVE_TOL;
    if both_open {
        return thrusters_temperature_recovery_st(r);
    }
    if both_closed {
        let mix = r.leaf("thrustersTemperatureRecoveryMix", "Temperature")?;
        return Some(St {
            value: mix.value,
            ts: mix.ts,
        });
    }
    Some(St {
        value: None,
        ts: min_ts(&[&sw_fwd.ts, &sw_aft.ts]),
    })
}

fn thrusters_temperature_pre_cooler(r: &InputReader) -> Option<Value> {
    Some(temp_leaf(thrusters_temperature_pre_cooler_st(r)?))
}

/// `thrustersSeawaterExchanger`: heat and delta-T across the seawater exchanger,
/// from the pre-cooler (supply) and supply-sensor (return) temperatures, the
/// summed flow, and the exchanger mix valve. Mirrors the module's inline
/// formula (not the generic `HeatExchanger.from_sensors`).
fn thrusters_seawater_exchanger(r: &InputReader) -> Option<Value> {
    let supply = thrusters_temperature_pre_cooler_st(r)?;
    let return_ = r.leaf("thrustersTemperatureSupply", "Temperature")?;
    let flow = thrusters_flow_st(r)?;
    let mix = r.leaf("thrustersMixExchanger", "PositionRel")?;

    let supply_truthy = truthy(supply.value);
    let (sv, rv, mv, fv) = (
        supply.value.unwrap_or(0.0),
        return_.value.unwrap_or(0.0),
        mix.value.unwrap_or(0.0),
        flow.value.unwrap_or(0.0),
    );

    let delta_t_value = if supply_truthy {
        if mv > 0.0 {
            (1.0 / mv) * (rv - sv)
        } else {
            0.0
        }
    } else {
        0.0
    };
    let delta_t_ts = min_ts(&[&supply.ts, &return_.ts]);

    let heat_value =
        fv * (if supply_truthy { rv - sv } else { 0.0 }) * WATER_HEAT_TRANSFER_CONVERSION;
    let heat_ts = min_ts(&[&return_.ts, &supply.ts, &flow.ts]);

    Some(json!({
        "Heat": leaf_json(Some(heat_value), &heat_ts),
        "DeltaT": leaf_json(Some(delta_t_value), &delta_t_ts),
    }))
}

// ---------------------------------------------------------------------------
// dhw
//
// dhw's computed fields reuse three generic THRS constructors:
//   * `TemperatureDelta.from_temperature_sensors` -> `temperature_delta`
//   * `HeatTransferDevice.from_sensors` (HeatExchanger/HeatPump/HvacExchanger)
//     -> `heat_transfer`
//   * `CalculatedFlow` summed flow -> inline (like `thrusters_flow`)
// Three of them gate on valve positions (`valves_open_closed`); their off-branch
// is `Stamped.stamp(0)` == value 0 with `datetime.now(UTC)`, whose timestamp is
// non-reproducible even across two thrs-api reads. We reproduce exactly that
// (`zero_heat_transfer` stamps with `now_iso()`); the parity suites compare
// such timestamps with a tolerance.
// ---------------------------------------------------------------------------

/// `HeatTransferDevice.from_sensors`: `{DeltaT, Heat}` where
/// `deltaT = return - supply` (0.0 if either reading is null) and
/// `heat = flow * deltaT * conversion`. Timestamps follow `Stamped.combine`
/// (min): deltaT over (supply, return), heat over (supply, return, flow).
fn heat_transfer(supply: &St, return_: &St, flow: &St) -> Value {
    let delta_value = match (supply.value, return_.value) {
        (Some(s), Some(r)) => r - s,
        _ => 0.0,
    };
    let delta_ts = min_ts(&[&supply.ts, &return_.ts]);
    let heat_value = flow.value.unwrap_or(0.0) * delta_value * WATER_HEAT_TRANSFER_CONVERSION;
    let heat_ts = min_ts(&[&supply.ts, &return_.ts, &flow.ts]);
    json!({
        "DeltaT": leaf_json(Some(delta_value), &delta_ts),
        "Heat": leaf_json(Some(heat_value), &heat_ts),
    })
}

/// `TemperatureDelta.from_temperature_sensors`: `{DeltaT}` = `return - supply`,
/// carrying the min of the two temperature timestamps. Null when either reading
/// is null (thrs-api relies on both being present here).
fn temperature_delta(supply: &St, return_: &St) -> Value {
    let value = match (supply.value, return_.value) {
        (Some(s), Some(r)) => Some(r - s),
        _ => None,
    };
    json!({ "DeltaT": leaf_json(value, &min_ts(&[&supply.ts, &return_.ts])) })
}

/// `HeatExchanger(delta_t=Stamped.stamp(0), heat=Stamped.stamp(0))` for a
/// heat-transfer device whose valve gate is off: value 0 with a read-time `now()`
/// timestamp, exactly like thrs-api (whose timestamp there changes every read).
fn zero_heat_transfer() -> Value {
    let ts = now_iso();
    json!({
        "DeltaT": leaf_json(Some(0.0), &ts),
        "Heat": leaf_json(Some(0.0), &ts),
    })
}

/// `sensor.valves_open_closed`: every `open` valve reads open (> 1 - tol) and
/// every `closed` valve reads closed (< 0 + tol). A missing reading counts as 0.
fn valves_open_closed(open: &[&St], closed: &[&St]) -> bool {
    open.iter()
        .all(|v| v.value.unwrap_or(0.0) > 1.0 - VALVE_TOL)
        && closed.iter().all(|v| v.value.unwrap_or(0.0) < VALVE_TOL)
}

fn dhw_delta(r: &InputReader, supply_field: &str, return_field: &str) -> Option<Value> {
    let supply = r.leaf(supply_field, "Temperature")?;
    let return_ = r.leaf(return_field, "Temperature")?;
    Some(temperature_delta(&supply, &return_))
}

fn dhw_exchanger(
    r: &InputReader,
    supply_field: &str,
    return_field: &str,
    flow_field: &str,
) -> Option<Value> {
    let supply = r.leaf(supply_field, "Temperature")?;
    let return_ = r.leaf(return_field, "Temperature")?;
    let flow = r.leaf(flow_field, "Flow")?;
    Some(heat_transfer(&supply, &return_, &flow))
}

/// `dhwFreshwaterFlowSupply` = `dhw_flow_drives.flow + dhw_flow_dc.flow`.
fn dhw_freshwater_flow_supply(r: &InputReader) -> Option<Value> {
    Some(flow_leaf(flow_sum(
        r,
        &[("dhwFlowDrives", "Flow"), ("dhwFlowDc", "Flow")],
    )?))
}

const DHW_SWITCH_HEATPUMP: &str = "dhwSwitchHeatpump";
const DHW_SWITCH_HIGH: &str = "dhwSwitchHighTemperature";
const DHW_SWITCH_LOW: &str = "dhwSwitchLowTemperature";

/// A heat exchanger on the boosting circuit, gated on the three dhw switches:
/// when `open` reads open and every `closed` reads closed, the exchanger is
/// `from_sensors` over boosting supply/return and the boosting flow; otherwise
/// the zeroed device. `dhwHeatpump` and `dhwConsumersExchanger` are this with
/// the switch roles swapped.
fn dhw_boosting_exchanger(r: &InputReader, open: &str, closed: [&str; 2]) -> Option<Value> {
    let open = r.leaf(open, "PositionRel")?;
    let closed_a = r.leaf(closed[0], "PositionRel")?;
    let closed_b = r.leaf(closed[1], "PositionRel")?;
    if valves_open_closed(&[&open], &[&closed_a, &closed_b]) {
        return dhw_exchanger(
            r,
            "dhwTemperatureBoostingSupply",
            "dhwTemperatureBoostingReturn",
            "dhwFlowBoosting",
        );
    }
    Some(zero_heat_transfer())
}

fn dhw_heatpump(r: &InputReader) -> Option<Value> {
    dhw_boosting_exchanger(r, DHW_SWITCH_HEATPUMP, [DHW_SWITCH_HIGH, DHW_SWITCH_LOW])
}

fn dhw_consumers_exchanger(r: &InputReader) -> Option<Value> {
    dhw_boosting_exchanger(r, DHW_SWITCH_HIGH, [DHW_SWITCH_HEATPUMP, DHW_SWITCH_LOW])
}

fn dhw_drives_exchanger(r: &InputReader) -> Option<Value> {
    let low = r.leaf(DHW_SWITCH_LOW, "PositionRel")?;
    // Low-temperature switch closed: freshwater-supply / drives-return over the
    // drives flow.
    if valves_open_closed(&[], &[&low]) {
        return dhw_exchanger(
            r,
            "dhwTemperatureFreshwaterSupply",
            "dhwTemperatureDrivesReturn",
            "dhwFlowDrives",
        );
    }
    let heatpump = r.leaf(DHW_SWITCH_HEATPUMP, "PositionRel")?;
    let high = r.leaf(DHW_SWITCH_HIGH, "PositionRel")?;
    let flowcontrol = r.leaf("dhwFlowcontrolDrives", "PositionRel")?;
    // Low-temperature switch open (others closed): boosting-supply / drives-return
    // over the boosting flow.
    if valves_open_closed(&[&low], &[&heatpump, &high, &flowcontrol]) {
        return dhw_exchanger(
            r,
            "dhwTemperatureBoostingSupply",
            "dhwTemperatureDrivesReturn",
            "dhwFlowBoosting",
        );
    }
    Some(zero_heat_transfer())
}

// ---------------------------------------------------------------------------
// pvt
//
// pvt's 19 computed fields form a small dependency graph over the raw string
// sensors: per string-group (main-aft strings 1-6, main-fwd strings 7-13,
// owners strings 1-6) a max/weighted temperature and a summed flow, then a
// `Pvt` heat-transfer per group, and finally a total flow, a seawater-exchanger
// flow and its heat exchanger. Everything is recomputed from raw leaves so it
// matches thrs-api's live value rather than a possibly-stale relay.
//
// Two raw inputs (`pvt_flow_main_string1_2` and
// `pvt_temperature_main_string1_2_return`) are the snake->camel collision
// shadows: they are addressed by their snake `gqlField` (see
// `build_module_view`'s `inputOnly`), so we read them by that name here.
// ---------------------------------------------------------------------------

/// Read a list of `(gqlField, leaf_raw)` inputs, or `None` if any is absent -
/// matching thrs-api, whose whole `sensorValues` model is all-or-nothing.
fn read_all(r: &InputReader, specs: &[(&str, &str)]) -> Option<Vec<St>> {
    specs.iter().map(|(f, l)| r.leaf(f, l)).collect()
}

fn min_ts_of(stamps: &[St]) -> String {
    let refs: Vec<&str> = stamps.iter().map(|s| s.ts.as_str()).collect();
    min_ts(&refs)
}

/// `CalculatedTemperature.from_max_temperature`: the value and *own* timestamp
/// of the hottest sensor (not a min-combine - thrs-api keeps the max sensor's
/// stamp).
fn max_temperature(r: &InputReader, temps: &[(&str, &str)]) -> Option<St> {
    let stamps = read_all(r, temps)?;
    stamps
        .into_iter()
        .max_by(|a, b| {
            a.value
                .unwrap_or(f64::NEG_INFINITY)
                .total_cmp(&b.value.unwrap_or(f64::NEG_INFINITY))
        })
        .map(|s| St {
            value: s.value,
            ts: s.ts,
        })
}

/// `weighted_combined_measurement`: flow-weighted average of `measurements`,
/// `None` (the temperature default) when the total weight is zero. The timestamp
/// is `Stamped.combine` over *all* weights and measurements (min), computed even
/// when the value is the zero-weight default.
fn weighted_temperature(
    r: &InputReader,
    weights: &[(&str, &str)],
    measurements: &[(&str, &str)],
) -> Option<St> {
    let w = read_all(r, weights)?;
    let m = read_all(r, measurements)?;
    let total: f64 = w.iter().map(|s| s.value.unwrap_or(0.0)).sum();
    let value = if total == 0.0 {
        None
    } else {
        let weighted: f64 = w
            .iter()
            .zip(m.iter())
            .map(|(wi, mi)| wi.value.unwrap_or(0.0) * mi.value.unwrap_or(0.0))
            .sum();
        Some(weighted / total)
    };
    let mut all = w;
    all.extend(m);
    Some(St {
        value,
        ts: min_ts_of(&all),
    })
}

/// `CalculatedFlow.from_sensors` / `from_summed_sensors`: sum of flows, min
/// timestamp.
fn flow_sum(r: &InputReader, flows: &[(&str, &str)]) -> Option<St> {
    let stamps = read_all(r, flows)?;
    let value: f64 = stamps.iter().map(|s| s.value.unwrap_or(0.0)).sum();
    Some(St {
        value: Some(value),
        ts: min_ts_of(&stamps),
    })
}

// Raw-input tables per string group. `L` = the loser (input-only) shadow read
// by its snake name.
const PVT_AFT_FLOWS: [(&str, &str); 10] = [
    ("pvtFlowMainString11", "Flow"),
    ("pvt_flow_main_string1_2", "Flow"),
    ("pvtFlowMainString21", "Flow"),
    ("pvtFlowMainString22", "Flow"),
    ("pvtFlowMainString3", "Flow"),
    ("pvtFlowMainString4", "Flow"),
    ("pvtFlowMainString51", "Flow"),
    ("pvtFlowMainString52", "Flow"),
    ("pvtFlowMainString61", "Flow"),
    ("pvtFlowMainString62", "Flow"),
];
const PVT_AFT_RETURN_TEMPS: [(&str, &str); 10] = [
    ("pvtTemperatureMainString11Return", "Temperature"),
    ("pvt_temperature_main_string1_2_return", "Temperature"),
    ("pvtTemperatureMainString21Return", "Temperature"),
    ("pvtTemperatureMainString22Return", "Temperature"),
    ("pvtTemperatureMainString3Return", "Temperature"),
    ("pvtTemperatureMainString4Return", "Temperature"),
    ("pvtTemperatureMainString51Return", "Temperature"),
    ("pvtTemperatureMainString52Return", "Temperature"),
    ("pvtTemperatureMainString61Return", "Temperature"),
    ("pvtTemperatureMainString62Return", "Temperature"),
];
/// Supply temps paired with `PVT_AFT_FLOWS` for the weighted supply average
/// (some entries repeat, mirroring the model's paired strings).
const PVT_AFT_SUPPLY_TEMPS_WEIGHTED: [(&str, &str); 10] = [
    ("pvtTemperatureMainString1Supply", "Temperature"),
    ("pvtTemperatureMainString1Supply", "Temperature"),
    ("pvtTemperatureMainString2Supply", "Temperature"),
    ("pvtTemperatureMainString2Supply", "Temperature"),
    ("pvtTemperatureMainString3Supply", "Temperature"),
    ("pvtTemperatureMainString4Supply", "Temperature"),
    ("pvtTemperatureMainString5Supply", "Temperature"),
    ("pvtTemperatureMainString5Supply", "Temperature"),
    ("pvtTemperatureMainString6Supply", "Temperature"),
    ("pvtTemperatureMainString6Supply", "Temperature"),
];
const PVT_AFT_SUPPLY_TEMPS: [(&str, &str); 6] = [
    ("pvtTemperatureMainString1Supply", "Temperature"),
    ("pvtTemperatureMainString2Supply", "Temperature"),
    ("pvtTemperatureMainString3Supply", "Temperature"),
    ("pvtTemperatureMainString4Supply", "Temperature"),
    ("pvtTemperatureMainString5Supply", "Temperature"),
    ("pvtTemperatureMainString6Supply", "Temperature"),
];

const PVT_FWD_FLOWS: [(&str, &str); 10] = [
    ("pvtFlowMainString71", "Flow"),
    ("pvtFlowMainString72", "Flow"),
    ("pvtFlowMainString81", "Flow"),
    ("pvtFlowMainString82", "Flow"),
    ("pvtFlowMainString9", "Flow"),
    ("pvtFlowMainString10", "Flow"),
    ("pvtFlowMainString111", "Flow"),
    ("pvtFlowMainString112", "Flow"),
    ("pvtFlowMainString12", "Flow"),
    ("pvtFlowMainString13", "Flow"),
];
const PVT_FWD_RETURN_TEMPS: [(&str, &str); 10] = [
    ("pvtTemperatureMainString71Return", "Temperature"),
    ("pvtTemperatureMainString72Return", "Temperature"),
    ("pvtTemperatureMainString81Return", "Temperature"),
    ("pvtTemperatureMainString82Return", "Temperature"),
    ("pvtTemperatureMainString9Return", "Temperature"),
    ("pvtTemperatureMainString10Return", "Temperature"),
    ("pvtTemperatureMainString111Return", "Temperature"),
    ("pvtTemperatureMainString112Return", "Temperature"),
    ("pvtTemperatureMainString12Return", "Temperature"),
    ("pvtTemperatureMainString13Return", "Temperature"),
];
const PVT_FWD_SUPPLY_TEMPS_WEIGHTED: [(&str, &str); 10] = [
    ("pvtTemperatureMainString7Supply", "Temperature"),
    ("pvtTemperatureMainString7Supply", "Temperature"),
    ("pvtTemperatureMainString8Supply", "Temperature"),
    ("pvtTemperatureMainString8Supply", "Temperature"),
    ("pvtTemperatureMainString9Supply", "Temperature"),
    ("pvtTemperatureMainString10Supply", "Temperature"),
    ("pvtTemperatureMainString11Supply", "Temperature"),
    ("pvtTemperatureMainString11Supply", "Temperature"),
    ("pvtTemperatureMainString12Supply", "Temperature"),
    ("pvtTemperatureMainString13Supply", "Temperature"),
];
const PVT_FWD_SUPPLY_TEMPS: [(&str, &str); 7] = [
    ("pvtTemperatureMainString7Supply", "Temperature"),
    ("pvtTemperatureMainString8Supply", "Temperature"),
    ("pvtTemperatureMainString9Supply", "Temperature"),
    ("pvtTemperatureMainString10Supply", "Temperature"),
    ("pvtTemperatureMainString11Supply", "Temperature"),
    ("pvtTemperatureMainString12Supply", "Temperature"),
    ("pvtTemperatureMainString13Supply", "Temperature"),
];

const PVT_OWNERS_FLOWS: [(&str, &str); 6] = [
    ("pvtFlowOwnersString1", "Flow"),
    ("pvtFlowOwnersString2", "Flow"),
    ("pvtFlowOwnersString3", "Flow"),
    ("pvtFlowOwnersString4", "Flow"),
    ("pvtFlowOwnersString5", "Flow"),
    ("pvtFlowOwnersString6", "Flow"),
];
const PVT_OWNERS_RETURN_TEMPS: [(&str, &str); 6] = [
    ("pvtTemperatureOwnersString1Return", "Temperature"),
    ("pvtTemperatureOwnersString2Return", "Temperature"),
    ("pvtTemperatureOwnersString3Return", "Temperature"),
    ("pvtTemperatureOwnersString4Return", "Temperature"),
    ("pvtTemperatureOwnersString5Return", "Temperature"),
    ("pvtTemperatureOwnersString6Return", "Temperature"),
];
const PVT_OWNERS_SUPPLY_TEMPS: [(&str, &str); 6] = [
    ("pvtTemperatureOwnersString1Supply", "Temperature"),
    ("pvtTemperatureOwnersString2Supply", "Temperature"),
    ("pvtTemperatureOwnersString3Supply", "Temperature"),
    ("pvtTemperatureOwnersString4Supply", "Temperature"),
    ("pvtTemperatureOwnersString5Supply", "Temperature"),
    ("pvtTemperatureOwnersString6Supply", "Temperature"),
];

/// The three recovery flows feeding `pvt_total_flow` / `pvt_return_temperature`.
const PVT_RECOVERY_FLOWS: [(&str, &str); 3] = [
    ("pvtFlowMainAftRecovery", "Flow"),
    ("pvtFlowMainFwdRecovery", "Flow"),
    ("pvtFlowOwnersRecovery", "Flow"),
];
const PVT_RECOVERY_RETURN_TEMPS: [(&str, &str); 3] = [
    ("pvtTemperatureMainAftReturn", "Temperature"),
    ("pvtTemperatureMainFwdReturn", "Temperature"),
    ("pvtTemperatureOwnersReturn", "Temperature"),
];

fn temp_leaf(st: St) -> Value {
    json!({ "Temperature": leaf_json(st.value, &st.ts) })
}
fn flow_leaf(st: St) -> Value {
    json!({ "Flow": leaf_json(st.value, &st.ts) })
}

/// `pvt_max_temperature_*_strings` for a group's return+supply temps.
fn pvt_max_temperature(
    r: &InputReader,
    returns: &[(&str, &str)],
    supplies: &[(&str, &str)],
) -> Option<Value> {
    let mut all: Vec<(&str, &str)> = returns.to_vec();
    all.extend_from_slice(supplies);
    Some(temp_leaf(max_temperature(r, &all)?))
}

/// `pvt_total_flow`: sum of the three recovery flows.
fn pvt_total_flow_st(r: &InputReader) -> Option<St> {
    flow_sum(r, &PVT_RECOVERY_FLOWS)
}

/// `pvt_seawater_exchanger_flow` = `(1 - mix_exchanger.position_rel) *
/// total_flow`, over the min of the mix valve and total-flow timestamps.
fn pvt_seawater_exchanger_flow_st(r: &InputReader) -> Option<St> {
    let mix = r.leaf("pvtMixExchanger", "PositionRel")?;
    let total = pvt_total_flow_st(r)?;
    let value = (1.0 - mix.value.unwrap_or(0.0)) * total.value.unwrap_or(0.0);
    Some(St {
        value: Some(value),
        ts: min_ts(&[&mix.ts, &total.ts]),
    })
}

/// A ported formula: derives one computed field's payload (shaped exactly like
/// the relayed MQTT object) from the raw inputs, or `None` when an input isn't
/// cached.
type Formula = fn(&InputReader) -> Option<Value>;

/// The single table of ported (module, field) pairs and their formulas.
/// [`recompute_field`] runs the formula; [`is_recomputable`] only asks whether
/// there is one - both read this table, so they cannot drift apart.
fn formula(module: &str, gql_field: &str) -> Option<Formula> {
    let f: Formula = match (module, gql_field) {
        ("thrusters", "thrustersFlow") => thrusters_flow,
        ("thrusters", "thrustersTemperatureRecovery") => thrusters_temperature_recovery,
        ("thrusters", "thrustersTemperaturePreCooler") => thrusters_temperature_pre_cooler,
        ("thrusters", "thrustersSeawaterExchanger") => thrusters_seawater_exchanger,

        ("dhw", "drivesDelta") => |r| {
            dhw_delta(
                r,
                "drivesTemperatureRecovery",
                "drivesTemperatureRecoveryReturn",
            )
        },
        ("dhw", "dcDelta") => {
            |r| dhw_delta(r, "dcTemperatureRecovery", "dcTemperatureRecoveryReturn")
        }
        ("dhw", "consumersDelta") => |r| {
            dhw_delta(
                r,
                "consumersTemperatureDhwSupply",
                "consumersTemperatureDhwReturn",
            )
        },
        ("dhw", "adsorptionDelta") => |r| {
            dhw_delta(
                r,
                "adsorptionTemperatureWasteReturn",
                "adsorptionTemperatureDhwReturn",
            )
        },
        ("dhw", "dhwFreshwaterFlowSupply") => dhw_freshwater_flow_supply,
        ("dhw", "dhwHvacExchanger") => |r| {
            dhw_exchanger(
                r,
                "dhwTemperatureAdsorptionReturn",
                "dhwTemperatureHvacExchangerReturn",
                "dhwFlowDc",
            )
        },
        ("dhw", "dhwAdsorptionExchanger") => |r| {
            dhw_exchanger(
                r,
                "dhwTemperatureFreshwaterSupply",
                "dhwTemperatureAdsorptionReturn",
                "dhwFlowDc",
            )
        },
        ("dhw", "dhwDcExchanger") => |r| {
            dhw_exchanger(
                r,
                "dhwTemperatureHvacExchangerReturn",
                "dhwTemperatureDcReturn",
                "dhwFlowDc",
            )
        },
        ("dhw", "dhwHeatpump") => dhw_heatpump,
        ("dhw", "dhwConsumersExchanger") => dhw_consumers_exchanger,
        ("dhw", "dhwDrivesExchanger") => dhw_drives_exchanger,

        // pvt: max temperatures per string group (return + supply temps).
        ("pvt", "pvtMaxTemperatureMainAftStrings") => {
            |r| pvt_max_temperature(r, &PVT_AFT_RETURN_TEMPS, &PVT_AFT_SUPPLY_TEMPS)
        }
        ("pvt", "pvtMaxTemperatureMainFwdStrings") => {
            |r| pvt_max_temperature(r, &PVT_FWD_RETURN_TEMPS, &PVT_FWD_SUPPLY_TEMPS)
        }
        ("pvt", "pvtMaxTemperatureOwnersStrings") => {
            |r| pvt_max_temperature(r, &PVT_OWNERS_RETURN_TEMPS, &PVT_OWNERS_SUPPLY_TEMPS)
        }

        // pvt: flow-weighted supply/return temperatures per string group.
        ("pvt", "pvtTemperatureMainAftStringsSupply") => {
            |r| pvt_weighted(r, &PVT_AFT_FLOWS, &PVT_AFT_SUPPLY_TEMPS_WEIGHTED)
        }
        ("pvt", "pvtTemperatureMainFwdStringsSupply") => {
            |r| pvt_weighted(r, &PVT_FWD_FLOWS, &PVT_FWD_SUPPLY_TEMPS_WEIGHTED)
        }
        ("pvt", "pvtTemperatureOwnersStringsSupply") => {
            |r| pvt_weighted(r, &PVT_OWNERS_FLOWS, &PVT_OWNERS_SUPPLY_TEMPS)
        }
        ("pvt", "pvtTemperatureMainAftStringsReturn") => {
            |r| pvt_weighted(r, &PVT_AFT_FLOWS, &PVT_AFT_RETURN_TEMPS)
        }
        ("pvt", "pvtTemperatureMainFwdStringsReturn") => {
            |r| pvt_weighted(r, &PVT_FWD_FLOWS, &PVT_FWD_RETURN_TEMPS)
        }
        ("pvt", "pvtTemperatureOwnersStringsReturn") => {
            |r| pvt_weighted(r, &PVT_OWNERS_FLOWS, &PVT_OWNERS_RETURN_TEMPS)
        }

        // pvt: summed flow per string group.
        ("pvt", "pvtFlowMainAftStrings") => |r| Some(flow_leaf(flow_sum(r, &PVT_AFT_FLOWS)?)),
        ("pvt", "pvtFlowMainFwdStrings") => |r| Some(flow_leaf(flow_sum(r, &PVT_FWD_FLOWS)?)),
        ("pvt", "pvtFlowOwnersStrings") => |r| Some(flow_leaf(flow_sum(r, &PVT_OWNERS_FLOWS)?)),

        // pvt: return temperature (flow-weighted over the recovery flows).
        ("pvt", "pvtReturnTemperature") => {
            |r| pvt_weighted(r, &PVT_RECOVERY_FLOWS, &PVT_RECOVERY_RETURN_TEMPS)
        }
        ("pvt", "pvtTotalFlow") => |r| Some(flow_leaf(pvt_total_flow_st(r)?)),

        // pvt: per-group heat exchangers (Pvt = HeatTransferDevice).
        ("pvt", "pvtPvtMainAft") => |r| {
            pvt_group_exchanger(
                r,
                &PVT_AFT_FLOWS,
                &PVT_AFT_SUPPLY_TEMPS_WEIGHTED,
                &PVT_AFT_RETURN_TEMPS,
            )
        },
        ("pvt", "pvtPvtMainFwd") => |r| {
            pvt_group_exchanger(
                r,
                &PVT_FWD_FLOWS,
                &PVT_FWD_SUPPLY_TEMPS_WEIGHTED,
                &PVT_FWD_RETURN_TEMPS,
            )
        },
        ("pvt", "pvtPvtOwners") => |r| {
            pvt_group_exchanger(
                r,
                &PVT_OWNERS_FLOWS,
                &PVT_OWNERS_SUPPLY_TEMPS,
                &PVT_OWNERS_RETURN_TEMPS,
            )
        },

        // pvt: seawater exchanger flow and its heat exchanger.
        ("pvt", "pvtSeawaterExchangerFlow") => {
            |r| Some(flow_leaf(pvt_seawater_exchanger_flow_st(r)?))
        }
        ("pvt", "pvtSeawaterExchanger") => |r| {
            Some(heat_transfer(
                &r.leaf("pvtTemperatureSupply", "Temperature")?,
                &r.leaf("pcmTemperatureProducersSupply", "Temperature")?,
                &pvt_seawater_exchanger_flow_st(r)?,
            ))
        },

        _ => return None,
    };
    Some(f)
}

/// A flow-weighted temperature as a `{Temperature}` payload.
fn pvt_weighted(
    r: &InputReader,
    weights: &[(&str, &str)],
    measurements: &[(&str, &str)],
) -> Option<Value> {
    Some(temp_leaf(weighted_temperature(r, weights, measurements)?))
}

/// A string group's `Pvt` heat-transfer device: weighted supply/return
/// temperatures over the group's flows, and the summed flow.
fn pvt_group_exchanger(
    r: &InputReader,
    flows: &[(&str, &str)],
    supplies: &[(&str, &str)],
    returns: &[(&str, &str)],
) -> Option<Value> {
    Some(heat_transfer(
        &weighted_temperature(r, flows, supplies)?,
        &weighted_temperature(r, flows, returns)?,
        &flow_sum(r, flows)?,
    ))
}

/// Recompute one computed field's payload, or `None` when this (module, field)
/// isn't ported or an input is missing - the resolver then falls back to
/// relaying.
pub fn recompute_field(module: &str, gql_field: &str, reader: &InputReader) -> Option<Value> {
    formula(module, gql_field)?(reader)
}

/// Whether a (module, field) has a ported recompute formula.
pub fn is_recomputable(module: &str, gql_field: &str) -> bool {
    formula(module, gql_field).is_some()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn cache_with(entries: &[(&str, Value)]) -> Arc<TopicCache> {
        let cache = Arc::new(TopicCache::new());
        for (topic, val) in entries {
            cache.insert(topic, val.clone());
        }
        cache
    }

    fn topics() -> BTreeMap<String, String> {
        [
            ("thrustersFlowAft", "t/flow-aft"),
            ("thrustersFlowFwd", "t/flow-fwd"),
            ("thrustersTemperatureAft", "t/temp-aft"),
            ("thrustersTemperatureFwd", "t/temp-fwd"),
        ]
        .iter()
        .map(|(k, v)| (k.to_string(), v.to_string()))
        .collect()
    }

    #[test]
    fn flow_is_the_sum_with_min_timestamp() {
        let cache = cache_with(&[
            (
                "t/flow-aft",
                json!({"Flow": {"Value": 1.25, "TimeStamp": "2026-09-12T00:00:02Z"}}),
            ),
            (
                "t/flow-fwd",
                json!({"Flow": {"Value": 0.75, "TimeStamp": "2026-09-12T00:00:01Z"}}),
            ),
        ]);
        let topics = topics();
        let r = InputReader::new(&cache, &topics);
        let out = thrusters_flow(&r).unwrap();
        assert_eq!(out["Flow"]["Value"], json!(2.0));
        // Stamped.combine keeps the earliest timestamp.
        assert_eq!(out["Flow"]["TimeStamp"], json!("2026-09-12T00:00:01Z"));
    }

    #[test]
    fn recovery_is_flow_weighted_average_and_null_without_flow() {
        // 1.0*10 + 3.0*20 = 70, / 4.0 = 17.5
        let cache = cache_with(&[
            (
                "t/flow-aft",
                json!({"Flow": {"Value": 1.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
            ),
            (
                "t/flow-fwd",
                json!({"Flow": {"Value": 3.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
            ),
            (
                "t/temp-aft",
                json!({"Temperature": {"Value": 10.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
            ),
            (
                "t/temp-fwd",
                json!({"Temperature": {"Value": 20.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
            ),
        ]);
        let topics = topics();
        let r = InputReader::new(&cache, &topics);
        assert_eq!(
            thrusters_temperature_recovery(&r).unwrap()["Temperature"]["Value"],
            json!(17.5)
        );

        // No flow -> null (default_if_zero_weight=None).
        let cache0 = cache_with(&[
            (
                "t/flow-aft",
                json!({"Flow": {"Value": 0.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
            ),
            (
                "t/flow-fwd",
                json!({"Flow": {"Value": 0.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
            ),
            (
                "t/temp-aft",
                json!({"Temperature": {"Value": 10.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
            ),
            (
                "t/temp-fwd",
                json!({"Temperature": {"Value": 20.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
            ),
        ]);
        let r0 = InputReader::new(&cache0, &topics);
        assert_eq!(
            thrusters_temperature_recovery(&r0).unwrap()["Temperature"]["Value"],
            json!(null)
        );
    }

    #[test]
    fn pvt_max_temperature_keeps_hottest_sensor_value_and_own_timestamp() {
        // from_max_temperature keeps the max sensor's OWN timestamp (not a min).
        let cache = cache_with(&[
            (
                "t/a",
                json!({"Temperature": {"Value": 10.0, "TimeStamp": "2026-09-12T00:00:01Z"}}),
            ),
            (
                "t/b",
                json!({"Temperature": {"Value": 30.0, "TimeStamp": "2026-09-12T00:00:09Z"}}),
            ),
            (
                "t/c",
                json!({"Temperature": {"Value": 20.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
            ),
        ]);
        let topics: BTreeMap<String, String> = [("a", "t/a"), ("b", "t/b"), ("c", "t/c")]
            .iter()
            .map(|(k, v)| (k.to_string(), v.to_string()))
            .collect();
        let r = InputReader::new(&cache, &topics);
        let st = max_temperature(
            &r,
            &[
                ("a", "Temperature"),
                ("b", "Temperature"),
                ("c", "Temperature"),
            ],
        )
        .unwrap();
        assert_eq!(st.value, Some(30.0));
        assert_eq!(st.ts, "2026-09-12T00:00:09Z");
    }

    #[test]
    fn pvt_weighted_temperature_is_flow_weighted_and_null_without_flow() {
        let topics: BTreeMap<String, String> = [
            ("w1", "t/w1"),
            ("w2", "t/w2"),
            ("m1", "t/m1"),
            ("m2", "t/m2"),
        ]
        .iter()
        .map(|(k, v)| (k.to_string(), v.to_string()))
        .collect();
        // 1*10 + 3*20 = 70 / 4 = 17.5; timestamp = min over weights AND measurements.
        let cache = cache_with(&[
            (
                "t/w1",
                json!({"Flow": {"Value": 1.0, "TimeStamp": "2026-09-12T00:00:05Z"}}),
            ),
            (
                "t/w2",
                json!({"Flow": {"Value": 3.0, "TimeStamp": "2026-09-12T00:00:02Z"}}),
            ),
            (
                "t/m1",
                json!({"Temperature": {"Value": 10.0, "TimeStamp": "2026-09-12T00:00:04Z"}}),
            ),
            (
                "t/m2",
                json!({"Temperature": {"Value": 20.0, "TimeStamp": "2026-09-12T00:00:03Z"}}),
            ),
        ]);
        let r = InputReader::new(&cache, &topics);
        let st = weighted_temperature(
            &r,
            &[("w1", "Flow"), ("w2", "Flow")],
            &[("m1", "Temperature"), ("m2", "Temperature")],
        )
        .unwrap();
        assert_eq!(st.value, Some(17.5));
        assert_eq!(st.ts, "2026-09-12T00:00:02Z");

        // Zero total weight -> null value, timestamp still the min-combine.
        let cache0 = cache_with(&[
            (
                "t/w1",
                json!({"Flow": {"Value": 0.0, "TimeStamp": "2026-09-12T00:00:05Z"}}),
            ),
            (
                "t/w2",
                json!({"Flow": {"Value": 0.0, "TimeStamp": "2026-09-12T00:00:02Z"}}),
            ),
            (
                "t/m1",
                json!({"Temperature": {"Value": 10.0, "TimeStamp": "2026-09-12T00:00:04Z"}}),
            ),
            (
                "t/m2",
                json!({"Temperature": {"Value": 20.0, "TimeStamp": "2026-09-12T00:00:03Z"}}),
            ),
        ]);
        let r0 = InputReader::new(&cache0, &topics);
        let st0 = weighted_temperature(
            &r0,
            &[("w1", "Flow"), ("w2", "Flow")],
            &[("m1", "Temperature"), ("m2", "Temperature")],
        )
        .unwrap();
        assert_eq!(st0.value, None);
        assert_eq!(st0.ts, "2026-09-12T00:00:02Z");
    }

    #[test]
    fn pvt_missing_input_falls_back_to_relay() {
        // A required raw input absent from the cache -> None (resolver relays).
        let cache = cache_with(&[(
            "t/only",
            json!({"Flow": {"Value": 1.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
        )]);
        let topics: BTreeMap<String, String> = [("pvtFlowOwnersString1", "t/only")]
            .iter()
            .map(|(k, v)| (k.to_string(), v.to_string()))
            .collect();
        let r = InputReader::new(&cache, &topics);
        // pvtFlowOwnersStrings needs strings 1..6; only 1 is present.
        assert!(recompute_field("pvt", "pvtFlowOwnersStrings", &r).is_none());
    }

    #[test]
    fn now_iso_has_python_isoformat_shape() {
        let s = now_iso();
        // e.g. 2026-09-14T12:59:47.298746+00:00
        assert!(s.ends_with("+00:00"), "offset: {s}");
        assert_eq!(s.len(), 32, "len of {s}");
        assert_eq!(&s[4..5], "-");
        assert_eq!(&s[10..11], "T");
        assert_eq!(&s[19..20], ".");
        // Round-trips a plausible current year (sanity on the civil-date math).
        let year: i64 = s[0..4].parse().unwrap();
        assert!((2025..2100).contains(&year), "year {year} from {s}");
    }

    #[test]
    fn dhw_delta_is_return_minus_supply_with_min_timestamp() {
        let cache = cache_with(&[
            (
                "t/sup",
                json!({"Temperature": {"Value": 20.0, "TimeStamp": "2026-09-12T00:00:05Z"}}),
            ),
            (
                "t/ret",
                json!({"Temperature": {"Value": 32.5, "TimeStamp": "2026-09-12T00:00:03Z"}}),
            ),
        ]);
        let topics: BTreeMap<String, String> = [("sup", "t/sup"), ("ret", "t/ret")]
            .iter()
            .map(|(k, v)| (k.to_string(), v.to_string()))
            .collect();
        let r = InputReader::new(&cache, &topics);
        let out = temperature_delta(
            &r.leaf("sup", "Temperature").unwrap(),
            &r.leaf("ret", "Temperature").unwrap(),
        );
        assert_eq!(out["DeltaT"]["Value"], json!(12.5));
        assert_eq!(out["DeltaT"]["TimeStamp"], json!("2026-09-12T00:00:03Z"));
    }

    #[test]
    fn dhw_heatpump_computes_when_gated_open_and_zeroes_otherwise() {
        // heatpump switch open, high/low closed -> from_sensors branch.
        let base = |heatpump: f64| {
            cache_with(&[
                (
                    "t/hp",
                    json!({"PositionRel": {"Value": heatpump, "TimeStamp": "2026-09-12T00:00:00Z"}}),
                ),
                (
                    "t/high",
                    json!({"PositionRel": {"Value": 0.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
                ),
                (
                    "t/low",
                    json!({"PositionRel": {"Value": 0.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
                ),
                (
                    "t/bs",
                    json!({"Temperature": {"Value": 40.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
                ),
                (
                    "t/br",
                    json!({"Temperature": {"Value": 50.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
                ),
                (
                    "t/fb",
                    json!({"Flow": {"Value": 6.0, "TimeStamp": "2026-09-12T00:00:00Z"}}),
                ),
            ])
        };
        let topics: BTreeMap<String, String> = [
            ("dhwSwitchHeatpump", "t/hp"),
            ("dhwSwitchHighTemperature", "t/high"),
            ("dhwSwitchLowTemperature", "t/low"),
            ("dhwTemperatureBoostingSupply", "t/bs"),
            ("dhwTemperatureBoostingReturn", "t/br"),
            ("dhwFlowBoosting", "t/fb"),
        ]
        .iter()
        .map(|(k, v)| (k.to_string(), v.to_string()))
        .collect();

        let open = base(1.0);
        let r = InputReader::new(&open, &topics);
        let out = dhw_heatpump(&r).unwrap();
        assert_eq!(out["DeltaT"]["Value"], json!(10.0));
        // heat = flow(6) * deltaT(10) * (4184/60)
        assert_eq!(
            out["Heat"]["Value"],
            json!(6.0 * 10.0 * WATER_HEAT_TRANSFER_CONVERSION)
        );

        // heatpump switch closed -> gate off -> zeros.
        let closed = base(0.0);
        let r0 = InputReader::new(&closed, &topics);
        let out0 = dhw_heatpump(&r0).unwrap();
        assert_eq!(out0["DeltaT"]["Value"], json!(0.0));
        assert_eq!(out0["Heat"]["Value"], json!(0.0));
    }
}
