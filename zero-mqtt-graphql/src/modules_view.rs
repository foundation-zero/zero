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
//! Raw values are relayed from the cache. Computed fields are either relayed
//! from the controller topics THRS-control publishes them on, or recomputed
//! in-process from the raw leaves (`COMPUTED_MODE`, see `crate::recompute`).
//!
//! Every GraphQL type name in a spec is thrs-api's own (read off its Strawberry
//! schema by the generator), so the two schemas match by name; the loader
//! rejects a spec that lacks one.

use std::collections::BTreeMap;
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
    /// `String`. Selects the `Stamped<Inner>` wrapper type. Enum leaves carry
    /// `String` (thrs-api serializes the enum member name).
    #[serde(default = "default_leaf_type")]
    pub r#type: String,
    /// For an enum leaf: the wire-value -> member-name map (e.g. `"0" ->
    /// "LOCAL"`, `"off" -> "OFF"`). thrs-api (Strawberry) returns the member
    /// name; the raw MQTT payload carries the value, so the resolver translates
    /// the cached value through this map. `None` for non-enum leaves.
    #[serde(default, rename = "enumValues")]
    pub enum_values: Option<BTreeMap<String, String>>,
    /// For an enum leaf: thrs-api's GraphQL enum type name (the Python Enum
    /// class, e.g. `ControlMode`). The leaf's `value` is typed as that enum, so
    /// the schema matches thrs-api's; the members are `enum_values`' names.
    /// Present exactly when `enum_values` is (checked by [`load_module_views`]).
    #[serde(default, rename = "enumType")]
    pub enum_type: Option<String>,
    /// Whether the leaf's value is nullable in thrs-api's schema
    /// (`Stamped[X | None]`, or an optional leaf field).
    #[serde(default)]
    pub optional: bool,
    /// For a leaf of a per-topic (actuated) section whose device payload keys
    /// it differently than the model's alias (`CC_DutyPoint` for `Dutypoint`,
    /// `CC_Setpoint` for `Setpoint`): the key to read off the device payload.
    /// The section container re-keys it to `raw` so the component type is the
    /// same one the mutation return object uses. `None` when the keys agree.
    #[serde(default, rename = "actuatedRaw")]
    pub actuated_raw: Option<String>,
    /// The wire-shaped default (`{"Value": ..., "TimeStamp": ...}`) thrs-api
    /// serves when the payload lacks this leaf (a model field with a default,
    /// e.g. `Pump.control_mode`). `None` for a required leaf.
    #[serde(default)]
    pub default: Option<serde_json::Value>,
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
    /// thrs-api's Strawberry type name for the component (`SensorFlowSensorType`),
    /// shared wherever the class is reused.
    pub type_name: String,
    /// Whether thrs-api derives this field (a pydantic `computed_field`). Just
    /// for diagnostics; the view exposes derived and raw fields the same way.
    #[serde(default)]
    pub computed: bool,
    /// A raw sensor that a snake->camel collision shadows in thrs-api's schema
    /// (e.g. `pvt_flow_main_string1_2`, hidden by `pvt_flow_main_string12`).
    /// thrs-api serves no query field for it, so neither do we - but it is a
    /// real topic that computed recompute reads as an input, so it stays in the
    /// view (addressed by its snake `gqlField`) and in the topic map, just
    /// without a registered GraphQL field.
    #[serde(default)]
    pub input_only: bool,
}

/// One field of a whole-object read section (controlValues / parameters /
/// controllerState). Unlike a sensor field it has no topic of its own: the whole
/// section is one object on [`ObjectSectionDef::topic`], and this field is pulled
/// out by [`key`](Self::key). It is either a flat scalar (`type`, e.g. a
/// parameter `Float`/`[Float!]`) or a Stamped-leaf component (`leaves`, e.g. a
/// controlValues valve's `setpoint`).
#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct ObjectFieldDef {
    /// GraphQL field name under the section, e.g. `coolingFlow`.
    pub gql_field: String,
    /// Key in the cached object payload, e.g. `CoolingFlow` (parameters are
    /// PascalCase; controlValues are snake_case per its `to_snake` aliases).
    pub key: String,
    /// GraphQL scalar for a flat field: `Float`, `Int`, `Boolean`, or a list
    /// like `[Float!]`. `None` for a component field (see `leaves`).
    #[serde(default)]
    pub r#type: Option<String>,
    /// thrs-api's type name for a component field (`ControlPumpType`); `None`
    /// for a flat field (checked by [`load_module_views`]).
    #[serde(default)]
    pub type_name: Option<String>,
    /// A flat field that is nullable in thrs-api's schema (`X | None`).
    #[serde(default)]
    pub optional: bool,
    /// For a component of a per-topic section (thrs-api's actuated
    /// `controlValues`): the device topic whose cached payload backs this
    /// component, read with the leaves' (actuated) wire keys. `None` for a
    /// field of a whole-object section, which is read off the section object.
    #[serde(default)]
    pub topic: Option<String>,
    /// Stamped `{value, timestamp}` leaves for a component field. Empty for a
    /// flat field.
    #[serde(default)]
    pub leaves: Vec<ModuleLeafDef>,
}

/// A whole-object read section: one MQTT topic carrying the entire section
/// object, and the fields extracted from it. Mirrors thrs-api's
/// `ControlApiChannels` `manual-values`/`parameters`/`controller-state`
/// listeners. When the topic has no cached object the section resolves null,
/// exactly like thrs-api returning null for an unpublished section.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct ObjectSectionDef {
    /// MQTT topic whose cached JSON object backs every field of this section.
    /// Empty for a per-topic section, whose fields carry their own topics.
    #[serde(default)]
    pub topic: String,
    /// thrs-api's type name for the section (`ThrustersParametersType`).
    pub type_name: String,
    #[serde(default)]
    pub fields: Vec<ObjectFieldDef>,
}

impl ObjectFieldDef {
    /// The component type name of a Stamped-leaf field (see `type_name`).
    /// Panics on a flat field or an unvalidated spec, which
    /// [`load_module_views`] rules out.
    pub fn component_type_name(&self) -> &str {
        self.type_name
            .as_deref()
            .expect("component field carries thrs-api's type name (spec validated on load)")
    }
}

/// One field of a plain (non-Stamped) object, e.g. a control-mode model's
/// `mode: str` or a nested group (`pvt.aft`). Either a scalar `type` or a
/// nested `object`.
#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct PlainFieldDef {
    pub gql_field: String,
    /// By-alias key in the payload object, e.g. `BoostingMode`.
    pub key: String,
    #[serde(default)]
    pub r#type: Option<String>,
    #[serde(default)]
    pub object: Option<PlainObjectDef>,
    /// Nullable in thrs-api's schema (optional field or default).
    #[serde(default)]
    pub optional: bool,
}

/// A plain pydantic model as a GraphQL object: thrs-api's type name
/// (`<Class>Type`, shared wherever the class is reused) plus its fields. A model
/// without fields renders an `Empty: Void` placeholder like thrs-api.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct PlainObjectDef {
    pub type_name: String,
    #[serde(default)]
    pub fields: Vec<PlainFieldDef>,
}

/// The switching control mode section (`controlMode { automatic automaticMode
/// {...} }`): one `SwitchingControlMode[M]` object on `topic`, whose `key`
/// (`AutomaticMode`) holds the module's mode model or null. `automatic` is
/// derived: the key is not null.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct ControlModeDef {
    #[serde(default)]
    pub topic: String,
    /// thrs-api's type name for the section (the `SwitchingControlMode[M]`
    /// specialisation, e.g. `...SwitchingControlModeType`).
    pub type_name: String,
    pub key: String,
    #[serde(default)]
    pub automatic_mode: PlainObjectDef,
}

/// A module-view spec file: every read section of one THRS module the UI queries
/// (`modules.<module>.{sensorValues,controlValues,parameters,controllerState}`).
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct ModuleView {
    /// Module name as it appears under `modules`, e.g. `thrusters`.
    pub module: String,
    /// thrs-api's type name for the `modules` object (`ControlModules`); the
    /// same in every view.
    pub modules_type_name: String,
    /// thrs-api's type name for this module's object (the `ControlModule[...]`
    /// specialisation).
    pub type_name: String,
    /// thrs-api's type name for the sensorValues object (`ThrustersSensorValuesType`).
    pub sensor_values_type_name: String,
    #[serde(default)]
    pub sensor_values: Vec<ModuleFieldDef>,
    /// The actuated control values (`controlValues`). The sections are
    /// optional so a partial view (tests) can leave them out.
    #[serde(default)]
    pub control_values: Option<ObjectSectionDef>,
    /// The controller parameters object (`parameters`).
    #[serde(default)]
    pub parameters: Option<ObjectSectionDef>,
    /// The controller-state object (`controllerState`).
    #[serde(default)]
    pub controller_state: Option<ObjectSectionDef>,
    /// The switching control mode (`controlMode`).
    #[serde(default)]
    pub control_mode: Option<ControlModeDef>,
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
            let view: ModuleView = serde_json::from_str(&content)
                .with_context(|| format!("failed to parse {display}"))?;
            validate_view(&view).with_context(|| format!("invalid module view {display}"))?;
            Ok(view)
        })
        .collect()
}

/// The spec invariants the resolvers rely on: an enum leaf names its enum type
/// and a Stamped-leaf section field names its component type.
fn validate_view(view: &ModuleView) -> anyhow::Result<()> {
    let sensor_leaves = view.sensor_values.iter().flat_map(|f| f.leaves.iter());
    let sections = [
        &view.control_values,
        &view.parameters,
        &view.controller_state,
    ]
    .into_iter()
    .flatten();
    for field in sections.flat_map(|s| s.fields.iter()) {
        if !field.leaves.is_empty() && field.type_name.is_none() {
            anyhow::bail!("component field '{}' has no typeName", field.gql_field);
        }
    }
    let section_leaves = [
        &view.control_values,
        &view.parameters,
        &view.controller_state,
    ]
    .into_iter()
    .flatten()
    .flat_map(|s| s.fields.iter())
    .flat_map(|f| f.leaves.iter());
    validate_enum_leaves(sensor_leaves.chain(section_leaves))
}

/// Every leaf with `enumValues` must carry `enumType` (and vice versa).
pub fn validate_enum_leaves<'a>(
    leaves: impl Iterator<Item = &'a ModuleLeafDef>,
) -> anyhow::Result<()> {
    for leaf in leaves {
        if leaf.enum_values.is_some() != leaf.enum_type.is_some() {
            anyhow::bail!(
                "enum leaf '{}' needs both enumType and enumValues",
                leaf.gql
            );
        }
    }
    Ok(())
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
        assert!(is_module_view_file(Path::new(
            "/specs/thrs-thrusters-module.json"
        )));
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
              "modulesTypeName": "ControlModules",
              "typeName": "ThrustersControlModule",
              "sensorValuesTypeName": "ThrustersSensorValuesType",
              "sensorValues": [
                {
                  "gqlField": "thrustersFlowAft",
                  "typeName": "SensorFlowSensorType",
                  "topic": "simulation/500000-thrs/thrusters/thrusters-flow-aft",
                  "leaves": [
                    {"gql": "flow", "raw": "Flow", "type": "Float"},
                    {"gql": "temperature", "raw": "Temperature", "type": "Float"},
                    {"gql": "quantity", "raw": "Quantity", "type": "Float"}
                  ]
                },
                {
                  "gqlField": "thrustersFlowcontrolAft",
                  "typeName": "SensorValveType",
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
        write_file(
            &dir,
            "thrs-thrusters-sensors-metadata.json",
            r#"{"group":"x","topics":[]}"#,
        );
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
        let leaf: ModuleLeafDef = serde_json::from_str(r#"{"gql":"flow","raw":"Flow"}"#).unwrap();
        assert_eq!(leaf.r#type, "Float");
    }

    #[test]
    fn test_load_module_views_missing_dir_errors() {
        assert!(load_module_views("/nonexistent-specs-xyz").is_err());
    }
}
