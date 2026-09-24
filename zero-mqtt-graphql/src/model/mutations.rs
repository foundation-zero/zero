use std::collections::BTreeMap;

use serde::Deserialize;

use crate::model_validation::ModelSchema;

use crate::extension::OperationRef;

/// Single-field numeric bounds a `setField` value must satisfy.
#[derive(Debug, Clone, Deserialize, PartialEq, Default)]
#[serde(rename_all = "camelCase")]
pub struct Bounds {
    pub min: Option<f64>,
    pub max: Option<f64>,
    pub exclusive_min: Option<f64>,
    pub exclusive_max: Option<f64>,
}

/// One unstamped leaf of a `setComponent` input; restamped with `now()` on write.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct InputFieldDef {
    /// GraphQL input-field name, e.g. `dutypoint`.
    pub gql: String,
    /// By-alias wire key written into the component object, e.g. `Dutypoint`.
    pub key: String,
    /// GraphQL scalar: `Float`, `Int`, `Boolean`, or `String` for an enum leaf.
    pub r#type: String,
    /// Enum leaf: wire value -> member name; the input takes the name, the wire stores the value.
    pub enum_values: Option<BTreeMap<String, String>>,
    /// Enum leaf: the enum type name. Present exactly when `enum_values` is.
    pub enum_type: Option<String>,
    /// Non-null in the API's input type.
    pub required: bool,
}

/// Source of one derived leaf: a component's stamped leaf, or a constant.
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

/// The comparison of an [`InvariantDef`].
#[derive(Debug, Clone, Copy, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub enum Comparison {
    Lt,
    Le,
    Gt,
    Ge,
}

impl Comparison {
    pub fn holds(self, lhs: f64, rhs: f64) -> bool {
        match self {
            Comparison::Lt => lhs < rhs,
            Comparison::Le => lhs <= rhs,
            Comparison::Gt => lhs > rhs,
            Comparison::Ge => lhs >= rhs,
        }
    }
}

/// A schema `x-invariants` entry: `object[lhs] <op> object[rhs]` must hold, else `error`.
#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct InvariantDef {
    pub lhs: String,
    pub op: Comparison,
    pub rhs: String,
    pub error: String,
}

impl InvariantDef {
    /// The error if `object` violates it; missing or non-numeric keys never do.
    pub fn violation(&self, object: &serde_json::Map<String, serde_json::Value>) -> Option<&str> {
        let number = |key: &str| object.get(key).and_then(serde_json::Value::as_f64);
        match (number(&self.lhs), number(&self.rhs)) {
            (Some(lhs), Some(rhs)) if !self.op.holds(lhs, rhs) => Some(&self.error),
            _ => None,
        }
    }
}

/// How a mutation waits for its change to show up on `topic` under `key` before returning.
/// With `presence` the Boolean argument is compared with whether `key` is non-null.
#[derive(Debug, Clone, PartialEq)]
pub struct ConfirmDef {
    pub operation: Option<OperationRef>,
    pub topic: String,
    pub key: Option<String>,
    pub presence: bool,
    pub timeout_s: f64,
    pub timeout_error: String,
}

/// `setField` overwrites one key, `setComponent` restamps one component, `setFlag` publishes a fresh object.
#[derive(Debug, Clone, Copy, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub enum MutationKind {
    SetField,
    SetComponent,
    SetFlag,
}

/// One mutation, published to `target` and (except `setFlag`) built from the cached `state` object.
#[derive(Debug, Clone, PartialEq)]
pub struct MutationDef {
    /// GraphQL mutation field name, e.g. `thrustersParameterSetCoolingFlow`.
    pub gql: String,
    pub kind: MutationKind,
    /// `setField`: GraphQL argument type, e.g. `Float` or `[Float!]`. Empty otherwise.
    pub arg_type: String,
    /// Name of the GraphQL argument.
    pub arg_name: String,
    /// By-alias key in the object to overwrite (`setField`/`setComponent`), or
    /// the key of the fresh object (`setFlag`).
    pub key: String,
    /// `setField`/`setComponent`: the `send` operation whose messages carry
    /// the object to modify.
    pub state: Option<OperationRef>,
    /// The `receive` operation the object is published to.
    pub target: Option<OperationRef>,
    /// The resolved topic of `state` (empty for `setFlag`).
    pub state_topic: String,
    /// The resolved topic of `target`.
    pub set_topic: String,
    /// The `object` section of the member the mutation returns. None returns
    /// `Boolean!`.
    pub returns: Option<String>,
    /// `setFlag`: the `key` value when the Boolean argument is true.
    pub true_value: Option<String>,
    /// `setFlag`: the `key` value when the Boolean argument is false.
    pub false_value: Option<String>,
    /// `setComponent`: the input leaves to restamp into the component.
    pub input_fields: Vec<InputFieldDef>,
    /// `setComponent`: mirror fields re-derived so the payload matches what the producer publishes.
    pub derived: Vec<DerivedFieldDef>,
    /// `setComponent`: the composite input type name, e.g. `PumpInputType`.
    pub input_type_name: Option<String>,
    /// The error when nothing is cached at the state topic to modify.
    pub missing_error: Option<String>,
    /// How the change is confirmed before the mutation returns; `None`
    /// returns right after the publish.
    pub confirm: Option<ConfirmDef>,
    /// `setField`/`setComponent`: the [`ModelSchema`] the written value is validated against.
    pub model: Option<ModelSchema>,
}

impl MutationDef {
    /// Whether this kind takes a composite component input.
    pub fn has_composite_input(&self) -> bool {
        self.kind == MutationKind::SetComponent
    }

    /// Whether this kind reads a cached state object.
    pub fn reads_state(&self) -> bool {
        self.kind != MutationKind::SetFlag
    }

    /// The composite input type name; panics for non-`setComponent` kinds.
    pub fn input_type_name(&self) -> &str {
        self.input_type_name
            .as_deref()
            .expect("composite mutation carries its input type name (spec validated on load)")
    }

    /// The topic a confirmation is awaited on, if any.
    pub fn confirm_topic(&self) -> Option<&str> {
        self.confirm.as_ref().map(|c| c.topic.as_str())
    }
}

/// `returns` must name one of the member's `object` sections.
pub fn validate_mutation(def: &MutationDef, sections: &[&str]) -> anyhow::Result<()> {
    if let Some(returns) = &def.returns {
        if !sections.contains(&returns.as_str()) {
            anyhow::bail!("mutation '{}' returns unknown section '{returns}'", def.gql);
        }
    }
    Ok(())
}
