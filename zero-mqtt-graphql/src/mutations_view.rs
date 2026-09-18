//! Write-path spec (`thrs-<module>-mutations.json`, from `print-module-mutations`).
//!
//! zero-mqtt-graphql is read-only by default; when `ENABLE_MUTATIONS` is set it
//! also serves thrs-api's module mutations 1:1 (see `build_module_mutations` in
//! `thrs.spec.asyncapi`, and `graphql::mutations` for the resolvers):
//!
//! * `parameter`: reads the current parameters object from `state_topic` in
//!   the cache, overwrites one by-alias key with the (bounds-checked) argument,
//!   and republishes the whole object to `set_topic`.
//! * `automationMode`: publishes a fresh `{"Mode": "automatic"|"manual"}`.
//! * `control`: restamps a composite unstamped input into one manual-values
//!   component and republishes the whole object.
//!
//! The simulation spec reuses [`MutationDef`] for its `simulation` input
//! mutations, which behave like `control`.

use std::collections::BTreeMap;
use std::path::Path;

use anyhow::Context;
use serde::Deserialize;

use crate::modules_view::ObjectSectionDef;

/// Suffix identifying a mutations spec file inside a spec directory.
pub const MUTATIONS_SUFFIX: &str = "-mutations.json";

/// Single-field numeric bounds a `parameter` mutation's value must satisfy,
/// mirroring the unit type's `Field(ge=/le=/gt=/lt=)` so mqtt-graphql rejects an
/// out-of-range value the way thrs-api's `validate_assignment` does. Cross-field
/// invariants (a parameter model's `model_validator`) are *not* represented here
/// - they are per-module domain logic still enforced by the control loop.
#[derive(Debug, Clone, Deserialize, PartialEq, Default)]
#[serde(rename_all = "camelCase")]
pub struct Bounds {
    pub min: Option<f64>,
    pub max: Option<f64>,
    pub exclusive_min: Option<f64>,
    pub exclusive_max: Option<f64>,
}

/// One field of a `control` mutation's composite input: an unstamped leaf of the
/// control component (`dutypoint`, `on`, `setpoint`, `controlMode`, ...). The
/// server restamps it with `now()` and writes `{wire_key: {Value, TimeStamp}}`.
#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct InputFieldDef {
    /// GraphQL input-field / argument name, e.g. `dutypoint`.
    pub arg_name: String,
    /// By-alias wire key written into the component object, e.g. `Dutypoint`.
    pub wire_key: String,
    /// GraphQL scalar: `Float`, `Int`, `Boolean`, or `String` for an enum leaf.
    pub r#type: String,
    /// For an enum leaf: wire-value -> member-name map. The input accepts the
    /// member name (a GraphQL enum); the wire stores the value (thrs-api's
    /// `use_enum_values`). `None` for a plain scalar.
    #[serde(default)]
    pub enum_values: Option<BTreeMap<String, String>>,
    /// For an enum leaf: thrs-api's enum type name (`PumpControlMode`), used as
    /// the input field's type so the schema matches thrs-api's. Present exactly
    /// when `enum_values` is (checked by [`validate_mutation`]).
    #[serde(default)]
    pub enum_type: Option<String>,
    /// Non-null in thrs-api's input type (a leaf with a nullable value or a
    /// default is nullable). Defaults to true for older specs.
    #[serde(default = "default_true")]
    pub required: bool,
}

fn default_true() -> bool {
    true
}

/// Where one leaf of a derived field comes from: copied from a component of
/// the same object and one of its stamped leaves (by-alias wire keys), or a
/// constant the model leaves at its default (`FlowSensor.quantity`).
#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", untagged)]
pub enum DerivedLeaf {
    Source { component: String, leaf: String },
    Constant { constant: serde_json::Value },
}

/// A field of the whole object that is a plain mirror of other components'
/// stamped leaves (see [`MutationDef::derived`]).
#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct DerivedFieldDef {
    /// By-alias key of the derived field in the whole object.
    pub key: String,
    /// By-alias leaf key -> where its value comes from.
    pub leaves: BTreeMap<String, DerivedLeaf>,
}

/// One mutation. Kinds: `parameter` (read-modify-republish one parameters
/// field), `automationMode` (publish a fresh `{"Mode": ...}`), `control`
/// (restamp a composite input into one manual-values component and republish)
/// and `simulation` (the same for a simulation inputs component).
#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct MutationDef {
    /// GraphQL mutation field name, e.g. `thrustersParameterSetCoolingFlow`
    /// (identical to thrs-api's Strawberry name).
    pub gql_name: String,
    /// Mutation family: `parameter`, `automationMode`, `control` or
    /// `simulation` (see the module docs).
    pub kind: String,
    /// GraphQL type of the argument: `Float`, `Int`, `Boolean`, or a list like
    /// `[Float!]` (a PID tuning tuple, non-null list arg). Unused by `control`
    /// (which has a composite input), so it defaults to empty there.
    #[serde(default)]
    pub arg_type: String,
    /// Name of the GraphQL argument (thrs-api's: `value`, or `automatic` for
    /// `automationMode`).
    pub arg_name: String,
    /// By-alias key in the cached payload to overwrite, e.g. `CoolingFlow`, or
    /// `Mode` for `automationMode`.
    pub payload_key: String,
    /// Topic whose cached payload holds the current object to modify
    /// (`parameter`). Unused by `automationMode`, which builds a fresh object.
    pub state_topic: String,
    /// Topic the object is published to.
    pub set_topic: String,
    /// Per-field numeric bounds (`parameter` only); `None` when the unit type
    /// declares no bound.
    #[serde(default)]
    pub bounds: Option<Bounds>,
    /// `automationMode`: the `payload_key` value when the Boolean arg is true.
    #[serde(default)]
    pub true_value: Option<String>,
    /// `automationMode`: the `payload_key` value when the Boolean arg is false.
    #[serde(default)]
    pub false_value: Option<String>,
    /// `control`/`simulation`: the composite input leaves to restamp into the
    /// component.
    #[serde(default)]
    pub input_fields: Vec<InputFieldDef>,
    /// `control`/`simulation`: fields of the whole object that thrs-api's
    /// model derives from other components (pydantic `computed_field`s that
    /// mirror a component's stamped leaves, e.g. dhw's `DrivesFlowRecovery`
    /// = `DhwDrivesSupply`'s flow and temperature). thrs-api re-serializes
    /// them from the modified model; the republish mirrors them the same way
    /// so the payload is identical.
    #[serde(default)]
    pub derived: Vec<DerivedFieldDef>,
    /// `control`/`simulation`: thrs-api's name for the composite input type
    /// (`PumpInputType`, shared across modules and simulations). zero-ui uses
    /// these names as GraphQL variable types, so they must match exactly.
    /// `None` for the other kinds (checked by [`validate_mutation`]).
    #[serde(default)]
    pub input_type_name: Option<String>,
    /// thrs-api's error when nothing is cached at `state_topic` to modify
    /// (`parameter`/`control`/`simulation`).
    #[serde(default)]
    pub missing_error: Option<String>,
}

impl MutationDef {
    /// Whether this kind takes a composite component input.
    pub fn has_composite_input(&self) -> bool {
        matches!(self.kind.as_str(), "control" | "simulation")
    }

    /// The composite input type name of a `control`/`simulation` mutation.
    /// Panics for other kinds or an unvalidated spec, which
    /// [`validate_mutation`] rules out.
    pub fn input_type_name(&self) -> &str {
        self.input_type_name.as_deref().expect(
            "composite mutation carries thrs-api's input type name (spec validated on load)",
        )
    }
}

/// The spec invariants the resolvers rely on: a composite mutation names its
/// input type, and an enum input field names its enum type.
pub fn validate_mutation(def: &MutationDef) -> anyhow::Result<()> {
    if def.has_composite_input() && def.input_type_name.is_none() {
        anyhow::bail!("mutation '{}' has no inputTypeName", def.gql_name);
    }
    for f in &def.input_fields {
        if f.enum_values.is_some() != f.enum_type.is_some() {
            anyhow::bail!(
                "mutation '{}': enum input '{}' needs both enumType and enumValues",
                def.gql_name,
                f.arg_name
            );
        }
    }
    Ok(())
}

/// A mutations spec file: every mutation of one THRS module, plus the objects
/// its mutations return: thrs-api returns the whole `Parameters` /
/// `ControlValues` model (the same `<Module>ParametersType` /
/// `<Module>ControlValuesType` the read sections serve), so both are the
/// module-view section shape and mqtt-graphql registers one type for read and
/// write. `control_values_object` is the manual-values object (plain aliases),
/// not the actuated read section.
#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct ModuleMutations {
    pub module: String,
    #[serde(default)]
    pub mutations: Vec<MutationDef>,
    #[serde(default)]
    pub parameters_object: ObjectSectionDef,
    #[serde(default)]
    pub control_values_object: ObjectSectionDef,
}

/// Whether this path is a mutations spec file (not an AsyncAPI document, a
/// topic-metadata file, nor a module-view file).
pub fn is_mutations_file(path: &Path) -> bool {
    path.file_name()
        .and_then(|name| name.to_str())
        .is_some_and(|name| name.ends_with(MUTATIONS_SUFFIX))
}

/// Load every `*-mutations.json` file from a spec directory, sorted by path so
/// schema output is deterministic. Missing directory or a malformed file is an
/// error (callers can downgrade to lenient).
pub fn load_mutations(spec_dir: &str) -> anyhow::Result<Vec<ModuleMutations>> {
    let dir = Path::new(spec_dir);
    if !dir.is_dir() {
        anyhow::bail!("spec_dir does not exist or is not a directory: {spec_dir}");
    }

    let mut paths: Vec<_> = std::fs::read_dir(dir)?
        .filter_map(|entry| entry.ok().map(|e| e.path()))
        .filter(|path| is_mutations_file(path))
        .collect();
    paths.sort();

    paths
        .into_iter()
        .map(|path| {
            let display = path.display().to_string();
            let content = std::fs::read_to_string(&path)
                .with_context(|| format!("failed to read {display}"))?;
            let module: ModuleMutations = serde_json::from_str(&content)
                .with_context(|| format!("failed to parse {display}"))?;
            for def in &module.mutations {
                validate_mutation(def).with_context(|| format!("invalid mutation in {display}"))?;
            }
            Ok(module)
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;

    #[test]
    fn test_is_mutations_file() {
        assert!(is_mutations_file(Path::new(
            "/specs/thrs-thrusters-mutations.json"
        )));
        assert!(!is_mutations_file(Path::new(
            "/specs/thrs-thrusters-module.json"
        )));
        assert!(!is_mutations_file(Path::new(
            "/specs/thrs-thrusters-sensors-metadata.json"
        )));
        assert!(!is_mutations_file(Path::new("/specs/thrs-control.json")));
    }

    #[test]
    fn test_load_mutations() {
        let dir = std::env::temp_dir().join("mqtt-graphql-mutations-test");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let mut file = std::fs::File::create(dir.join("thrs-thrusters-mutations.json")).unwrap();
        file.write_all(
            br#"{
              "module": "thrusters",
              "mutations": [
                {
                  "gqlName": "thrustersParameterSetCoolingFlow",
                  "kind": "parameter",
                  "argType": "Float",
                  "argName": "value",
                  "payloadKey": "CoolingFlow",
                  "stateTopic": "thrs/controller/thrusters/parameters",
                  "setTopic": "thrs/controller/thrusters/parameters/set"
                }
              ]
            }"#,
        )
        .unwrap();
        // A module-view file next to it must be ignored by this loader.
        std::fs::File::create(dir.join("thrs-thrusters-module.json"))
            .unwrap()
            .write_all(br#"{"module":"thrusters","sensorValues":[]}"#)
            .unwrap();

        let loaded = load_mutations(dir.to_str().unwrap()).unwrap();
        assert_eq!(loaded.len(), 1);
        assert_eq!(loaded[0].module, "thrusters");
        assert_eq!(loaded[0].mutations.len(), 1);
        let m = &loaded[0].mutations[0];
        assert_eq!(m.gql_name, "thrustersParameterSetCoolingFlow");
        assert_eq!(m.payload_key, "CoolingFlow");
        assert_eq!(m.set_topic, "thrs/controller/thrusters/parameters/set");

        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn test_load_mutations_missing_dir_errors() {
        assert!(load_mutations("/nonexistent-specs-xyz").is_err());
    }

    #[test]
    fn test_parameter_mutation_parses_bounds() {
        let m: MutationDef = serde_json::from_str(
            r#"{
              "gqlName": "thrustersParameterSetCoolingTemperature",
              "kind": "parameter",
              "argType": "Float",
              "argName": "value",
              "payloadKey": "CoolingTemperature",
              "stateTopic": "thrs/controller/thrusters/parameters",
              "setTopic": "thrs/controller/thrusters/parameters/set",
              "bounds": {"min": -273.15}
            }"#,
        )
        .unwrap();
        assert_eq!(m.arg_name, "value");
        assert_eq!(m.bounds.unwrap().min, Some(-273.15));
        assert!(m.true_value.is_none());
    }

    #[test]
    fn test_automation_mode_mutation_parses() {
        let m: MutationDef = serde_json::from_str(
            r#"{
              "gqlName": "thrustersSetAutomationMode",
              "kind": "automationMode",
              "argType": "Boolean",
              "argName": "automatic",
              "payloadKey": "Mode",
              "trueValue": "automatic",
              "falseValue": "manual",
              "stateTopic": "thrs/controller/thrusters/automation-mode",
              "setTopic": "thrs/controller/thrusters/automation-mode/set"
            }"#,
        )
        .unwrap();
        assert_eq!(m.kind, "automationMode");
        assert_eq!(m.arg_name, "automatic");
        assert_eq!(m.true_value.as_deref(), Some("automatic"));
        assert_eq!(m.false_value.as_deref(), Some("manual"));
    }
}
