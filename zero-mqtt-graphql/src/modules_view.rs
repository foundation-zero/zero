//! Nested per-module GraphQL view (`modules { <module> { sensorValues { ... } } }`).
//!
//! Our schema is flat (one query field per topic); the THRS UI wants the nested
//! shape thrs-api serves so it can migrate 1:1 (zero-ui `QUERY_ALL`). This
//! rebuilds that shape over the cache from the `thrs-<module>-module.json` specs
//! `print-module-view` emits. Each spec maps a sensor field to its topic and
//! lists the `{value, timestamp}` leaves with both names: the camelCase GraphQL
//! one and the raw PascalCase wire key. Both are needed because naming.rs
//! lowercases `PositionRel` to `positionrel` (and must, for power-tags), so THRS
//! hands us the mapping instead of us guessing it back.
//!
//! Values are relayed from the cache, never recomputed. Computed fields get
//! published by THRS-control on controller topics; we just relay those too.

use std::path::Path;

use anyhow::Context;
use serde::Deserialize;

/// Suffix identifying a module-view spec file inside a spec directory.
pub const MODULE_VIEW_SUFFIX: &str = "-module.json";

/// One `{value, timestamp}` leaf of a sensor field. Carries both names it goes
/// by: the camelCase GraphQL subfield (same as thrs-api) and the raw PascalCase
/// wire key it's stored under in the cached payload.
#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
pub struct ModuleLeafDef {
    /// GraphQL subfield name, e.g. `positionRel` (matches thrs-api).
    pub gql: String,
    /// Raw key in the cached MQTT payload, e.g. `PositionRel`.
    pub raw: String,
    /// Inner scalar of the `Stamped<T>` leaf: `Float`, `Boolean`, `Int` or
    /// `String`. Selects the `Stamped<Inner>` wrapper type.
    #[serde(default = "default_leaf_type")]
    pub r#type: String,
}

fn default_leaf_type() -> String {
    "Float".to_string()
}

/// One sensor field under `modules.<module>.sensorValues`, e.g.
/// `thrustersFlowAft`, resolved from a single MQTT topic.
#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct ModuleFieldDef {
    /// GraphQL field name under `sensorValues`, e.g. `thrustersFlowAft`.
    pub gql_field: String,
    /// Exact MQTT topic whose cached payload backs this field.
    pub topic: String,
    #[serde(default)]
    pub leaves: Vec<ModuleLeafDef>,
    /// Whether thrs-api derives this field (a pydantic `computed_field`). Just
    /// for diagnostics; the view exposes derived and raw fields the same way.
    #[serde(default)]
    pub computed: bool,
}

/// A module-view spec file: every `sensorValues` field of one THRS module.
#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct ModuleView {
    /// Module name as it appears under `modules`, e.g. `thrusters`.
    pub module: String,
    #[serde(default)]
    pub sensor_values: Vec<ModuleFieldDef>,
}

/// Whether this path is a module-view spec file (not an AsyncAPI document nor a
/// topic-metadata file).
pub fn is_module_view_file(path: &Path) -> bool {
    path.file_name()
        .and_then(|name| name.to_str())
        .is_some_and(|name| name.ends_with(MODULE_VIEW_SUFFIX))
}

/// Load every `*-module.json` module-view file from a spec directory, sorted by
/// path so schema output is deterministic. Missing directory or a malformed
/// file is an error (callers can downgrade to lenient).
pub fn load_module_views(spec_dir: &str) -> anyhow::Result<Vec<ModuleView>> {
    let dir = Path::new(spec_dir);
    if !dir.is_dir() {
        anyhow::bail!("spec_dir does not exist or is not a directory: {spec_dir}");
    }

    let mut paths: Vec<_> = std::fs::read_dir(dir)?
        .filter_map(|entry| entry.ok().map(|e| e.path()))
        .filter(|path| is_module_view_file(path))
        .collect();
    paths.sort();

    paths
        .into_iter()
        .map(|path| {
            let display = path.display().to_string();
            let content = std::fs::read_to_string(&path)
                .with_context(|| format!("failed to read {display}"))?;
            serde_json::from_str(&content).with_context(|| format!("failed to parse {display}"))
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;

    fn write_file(dir: &Path, name: &str, content: &str) {
        let mut file = std::fs::File::create(dir.join(name)).unwrap();
        file.write_all(content.as_bytes()).unwrap();
    }

    #[test]
    fn test_is_module_view_file() {
        assert!(is_module_view_file(Path::new("/specs/thrs-thrusters-module.json")));
        assert!(!is_module_view_file(Path::new(
            "/specs/thrs-thrusters-sensors-metadata.json"
        )));
        assert!(!is_module_view_file(Path::new("/specs/thrs-control.json")));
    }

    #[test]
    fn test_load_module_views() {
        let dir = std::env::temp_dir().join("mqtt-graphql-module-view-test");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();

        write_file(
            &dir,
            "thrs-thrusters-module.json",
            r#"{
              "module": "thrusters",
              "sensorValues": [
                {
                  "gqlField": "thrustersFlowAft",
                  "topic": "simulation/500000-thrs/thrusters/thrusters-flow-aft",
                  "leaves": [
                    {"gql": "flow", "raw": "Flow", "type": "Float"},
                    {"gql": "temperature", "raw": "Temperature", "type": "Float"},
                    {"gql": "quantity", "raw": "Quantity", "type": "Float"}
                  ]
                },
                {
                  "gqlField": "thrustersFlowcontrolAft",
                  "topic": "simulation/500000-thrs/thrusters/thrusters-flowcontrol-aft",
                  "leaves": [
                    {"gql": "positionRel", "raw": "PositionRel", "type": "Float"},
                    {"gql": "positionAbs", "raw": "PositionAbs", "type": "Float"}
                  ]
                }
              ]
            }"#,
        );
        // Adjacent metadata / asyncapi files must be ignored by this loader.
        write_file(&dir, "thrs-thrusters-sensors-metadata.json", r#"{"group":"x","topics":[]}"#);
        write_file(&dir, "thrs-control.json", r#"{"asyncapi":"3.0.0"}"#);

        let views = load_module_views(dir.to_str().unwrap()).unwrap();
        assert_eq!(views.len(), 1);
        let view = &views[0];
        assert_eq!(view.module, "thrusters");
        assert_eq!(view.sensor_values.len(), 2);
        assert_eq!(view.sensor_values[0].gql_field, "thrustersFlowAft");
        assert_eq!(view.sensor_values[0].leaves[0].raw, "Flow");
        assert_eq!(view.sensor_values[1].leaves[0].gql, "positionRel");
        assert_eq!(view.sensor_values[1].leaves[0].raw, "PositionRel");

        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn test_leaf_type_defaults_to_float() {
        let leaf: ModuleLeafDef =
            serde_json::from_str(r#"{"gql":"flow","raw":"Flow"}"#).unwrap();
        assert_eq!(leaf.r#type, "Float");
    }

    #[test]
    fn test_load_module_views_missing_dir_errors() {
        assert!(load_module_views("/nonexistent-specs-xyz").is_err());
    }
}
